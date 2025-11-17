"""
Session management for validation results.

This module provides session persistence and querying capabilities,
allowing validation results to be stored and retrieved across DCC sessions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from vfxvox_pipeline_utils.plugins.core.context import ValidationContext
from vfxvox_pipeline_utils.plugins.core.validator_interface import (
    IssueSeverity,
    ValidationIssue,
    ValidationResult,
)


@dataclass
class ValidationSession:
    """A validation session with results."""
    session_id: str
    created_at: datetime
    context: ValidationContext
    results: List[ValidationResult] = field(default_factory=list)
    
    def get_all_issues(self) -> List[ValidationIssue]:
        """Get all issues from all results."""
        issues = []
        for result in self.results:
            issues.extend(result.issues)
        return issues
        
    def get_issues_by_severity(
        self,
        severity: IssueSeverity
    ) -> List[ValidationIssue]:
        """Get issues filtered by severity."""
        return [i for i in self.get_all_issues() if i.severity == severity]
        
    def has_errors(self) -> bool:
        """Check if session has any errors."""
        return any(r.has_errors() for r in self.results)


@dataclass
class SessionFilters:
    """Filters for querying validation sessions."""
    user: Optional[str] = None
    project: Optional[str] = None
    dcc_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    has_errors: Optional[bool] = None


class SessionManager:
    """Manages validation sessions and persistence.
    
    The SessionManager handles:
    - Creating and managing validation sessions
    - Persisting sessions to disk
    - Loading sessions from disk
    - Querying sessions with filters
    - Exporting sessions to various formats
    
    Example:
        manager = SessionManager()
        session = manager.create_session(context)
        manager.add_result(session.session_id, result)
        
        # Query sessions
        sessions = manager.query_sessions(SessionFilters(user="john"))
        
        # Export session
        json_data = manager.export_session(session.session_id, format="json")
    """
    
    def __init__(self, storage_path: Optional[str] = None, auto_load: bool = True):
        """Initialize session manager with optional storage path.
        
        Args:
            storage_path: Optional path to store session files.
            auto_load: Whether to automatically load existing sessions.
        """
        self._storage_path = storage_path or self._get_default_storage_path()
        self._current_session: Optional[ValidationSession] = None
        self._sessions: Dict[str, ValidationSession] = {}
        self._max_history = 100  # Maximum number of sessions to keep in memory
        
        if auto_load:
            self._load_sessions()
        
    def create_session(
        self,
        context: ValidationContext,
        auto_persist: bool = True
    ) -> ValidationSession:
        """Create a new validation session.
        
        Args:
            context: Validation context for this session.
            auto_persist: Whether to automatically persist the session.
            
        Returns:
            New ValidationSession instance.
        """
        import uuid
        
        session = ValidationSession(
            session_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            context=context,
            results=[]
        )
        
        self._current_session = session
        self._sessions[session.session_id] = session
        
        if auto_persist:
            self._persist_session(session)
        
        # Cleanup old sessions if we exceed max history
        self._cleanup_old_sessions()
        
        return session
        
    def add_result(
        self,
        session_id: str,
        result: ValidationResult,
        auto_persist: bool = True
    ) -> None:
        """Add a validation result to a session.
        
        Args:
            session_id: ID of the session to add result to.
            result: Validation result to add.
            auto_persist: Whether to automatically persist the session.
            
        Raises:
            ValueError: If session is not found.
        """
        if session_id not in self._sessions:
            raise ValueError(f"Session {session_id} not found")
            
        self._sessions[session_id].results.append(result)
        
        if auto_persist:
            self._persist_session(self._sessions[session_id])
            
    def get_session(self, session_id: str, load_if_missing: bool = True) -> Optional[ValidationSession]:
        """Get a session by ID.
        
        Args:
            session_id: ID of the session to retrieve.
            load_if_missing: Whether to try loading from disk if not in memory.
            
        Returns:
            ValidationSession if found, None otherwise.
        """
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        if load_if_missing:
            session = self._load_session(session_id)
            if session:
                self._sessions[session_id] = session
                return session
        
        return None
    
    def get_current_session(self) -> Optional[ValidationSession]:
        """Get the current active session.
        
        Returns:
            Current ValidationSession or None.
        """
        return self._current_session
    
    def set_current_session(self, session_id: str) -> None:
        """Set the current active session.
        
        Args:
            session_id: ID of the session to set as current.
            
        Raises:
            ValueError: If session is not found.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        self._current_session = session
        
    def get_latest_session(
        self,
        scene_path: Optional[str] = None
    ) -> Optional[ValidationSession]:
        """Get the most recent session, optionally filtered by scene."""
        sessions = list(self._sessions.values())
        
        if scene_path:
            sessions = [s for s in sessions if s.context.scene_path == scene_path]
            
        if not sessions:
            return None
            
        return max(sessions, key=lambda s: s.created_at)
        
    def query_sessions(
        self,
        filters: SessionFilters
    ) -> List[ValidationSession]:
        """Query sessions with filters."""
        results = list(self._sessions.values())
        
        if filters.user:
            results = [s for s in results if s.context.user == filters.user]
            
        if filters.project:
            results = [s for s in results if s.context.project == filters.project]
            
        if filters.dcc_name:
            results = [s for s in results if s.context.dcc_name == filters.dcc_name]
            
        if filters.start_date:
            results = [s for s in results if s.created_at >= filters.start_date]
            
        if filters.end_date:
            results = [s for s in results if s.created_at <= filters.end_date]
            
        if filters.has_errors is not None:
            results = [s for s in results if s.has_errors() == filters.has_errors]
            
        return sorted(results, key=lambda s: s.created_at, reverse=True)
        
    def export_session(
        self,
        session_id: str,
        format: str = "json"
    ) -> str:
        """Export session to JSON or CSV."""
        import json
        from dataclasses import asdict
        
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        if format == "json":
            return json.dumps(asdict(session), indent=2, default=str)
        elif format == "csv":
            return self._export_to_csv(session)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def delete_session(self, session_id: str, delete_file: bool = True) -> bool:
        """Delete a session.
        
        Args:
            session_id: ID of the session to delete.
            delete_file: Whether to delete the session file from disk.
            
        Returns:
            True if session was deleted, False if not found.
        """
        if session_id not in self._sessions:
            return False
        
        # Remove from memory
        del self._sessions[session_id]
        
        # Clear current session if it was deleted
        if self._current_session and self._current_session.session_id == session_id:
            self._current_session = None
        
        # Delete file
        if delete_file:
            from pathlib import Path
            session_file = Path(self._storage_path) / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
        
        return True
    
    def list_session_ids(self) -> List[str]:
        """List all session IDs in memory.
        
        Returns:
            List of session IDs.
        """
        return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """Get the number of sessions in memory.
        
        Returns:
            Number of sessions.
        """
        return len(self._sessions)
    
    def clear_sessions(self, delete_files: bool = False) -> None:
        """Clear all sessions from memory.
        
        Args:
            delete_files: Whether to delete session files from disk.
        """
        if delete_files:
            from pathlib import Path
            storage_path = Path(self._storage_path)
            for session_file in storage_path.glob("*.json"):
                session_file.unlink()
        
        self._sessions.clear()
        self._current_session = None
    
    def _get_default_storage_path(self) -> str:
        """Get default storage path for sessions."""
        import os
        from pathlib import Path
        
        home = Path.home()
        storage_path = home / ".vfxvox" / "sessions"
        storage_path.mkdir(parents=True, exist_ok=True)
        
        return str(storage_path)
        
    def _persist_session(self, session: ValidationSession) -> None:
        """Persist session to disk.
        
        Args:
            session: Session to persist.
        """
        import json
        from dataclasses import asdict
        from pathlib import Path
        
        storage_path = Path(self._storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        session_file = storage_path / f"{session.session_id}.json"
        
        try:
            with open(session_file, "w") as f:
                json.dump(asdict(session), f, indent=2, default=str)
        except Exception as e:
            # Log error but don't fail
            print(f"Warning: Failed to persist session {session.session_id}: {e}")
    
    def _load_session(self, session_id: str) -> Optional[ValidationSession]:
        """Load a session from disk.
        
        Args:
            session_id: ID of the session to load.
            
        Returns:
            ValidationSession if found, None otherwise.
        """
        import json
        from pathlib import Path
        
        session_file = Path(self._storage_path) / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, "r") as f:
                data = json.load(f)
            
            # Reconstruct the session from JSON data
            return self._deserialize_session(data)
        except Exception as e:
            print(f"Warning: Failed to load session {session_id}: {e}")
            return None
    
    def _load_sessions(self, max_sessions: Optional[int] = None) -> None:
        """Load sessions from disk.
        
        Args:
            max_sessions: Maximum number of sessions to load (most recent).
        """
        from pathlib import Path
        
        storage_path = Path(self._storage_path)
        
        if not storage_path.exists():
            return
        
        # Get all session files
        session_files = list(storage_path.glob("*.json"))
        
        # Sort by modification time (most recent first)
        session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Limit number of sessions to load
        if max_sessions:
            session_files = session_files[:max_sessions]
        else:
            session_files = session_files[:self._max_history]
        
        # Load each session
        for session_file in session_files:
            session_id = session_file.stem
            session = self._load_session(session_id)
            if session:
                self._sessions[session_id] = session
    
    def _deserialize_session(self, data: Dict[str, Any]) -> ValidationSession:
        """Deserialize session data from JSON.
        
        Args:
            data: Session data dictionary.
            
        Returns:
            ValidationSession instance.
        """
        from vfxvox_pipeline_utils.plugins.core.context import (
            ValidationContext,
            ValidationScope,
            SceneElement,
            SceneInfo,
        )
        
        # Reconstruct context
        context_data = data["context"]
        scene_info_data = context_data["scene_info"]
        
        scene_info = SceneInfo(
            frame_range=tuple(scene_info_data["frame_range"]),
            current_frame=scene_info_data["current_frame"],
            fps=scene_info_data["fps"],
            units=scene_info_data["units"],
            up_axis=scene_info_data["up_axis"],
            file_format=scene_info_data["file_format"],
            is_saved=scene_info_data["is_saved"],
            is_modified=scene_info_data["is_modified"]
        )
        
        selection = [
            SceneElement(**elem_data)
            for elem_data in context_data["selection"]
        ]
        
        context = ValidationContext(
            context_id=context_data["context_id"],
            dcc_name=context_data["dcc_name"],
            dcc_version=context_data["dcc_version"],
            scene_path=context_data["scene_path"],
            selection=selection,
            scope=ValidationScope(context_data["scope"]),
            scene_info=scene_info,
            working_directory=context_data["working_directory"],
            output_directory=context_data["output_directory"],
            user=context_data["user"],
            project=context_data.get("project"),
            shot=context_data.get("shot"),
            metadata=context_data.get("metadata", {}),
            parameters=context_data.get("parameters", {})
        )
        
        # Reconstruct results
        results = []
        for result_data in data["results"]:
            issues = []
            for issue_data in result_data["issues"]:
                element = None
                if issue_data.get("element"):
                    element = SceneElement(**issue_data["element"])
                
                issue = ValidationIssue(
                    issue_id=issue_data["issue_id"],
                    severity=IssueSeverity(issue_data["severity"]),
                    category=issue_data["category"],
                    message=issue_data["message"],
                    description=issue_data["description"],
                    element=element,
                    location=issue_data.get("location"),
                    suggested_fix=issue_data.get("suggested_fix"),
                    can_auto_fix=issue_data.get("can_auto_fix", False),
                    documentation_url=issue_data.get("documentation_url"),
                    metadata=issue_data.get("metadata", {})
                )
                issues.append(issue)
            
            result = ValidationResult(
                validator_id=result_data["validator_id"],
                validator_name=result_data["validator_name"],
                context_id=result_data["context_id"],
                timestamp=datetime.fromisoformat(result_data["timestamp"]) if isinstance(result_data["timestamp"], str) else result_data["timestamp"],
                duration_seconds=result_data["duration_seconds"],
                issues=issues,
                metadata=result_data.get("metadata", {})
            )
            results.append(result)
        
        # Create session
        return ValidationSession(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            context=context,
            results=results
        )
    
    def _cleanup_old_sessions(self) -> None:
        """Remove old sessions from memory if exceeding max history."""
        if len(self._sessions) <= self._max_history:
            return
        
        # Sort sessions by creation time
        sorted_sessions = sorted(
            self._sessions.values(),
            key=lambda s: s.created_at,
            reverse=True
        )
        
        # Keep only the most recent sessions
        sessions_to_keep = {s.session_id for s in sorted_sessions[:self._max_history]}
        
        # Remove old sessions
        sessions_to_remove = [
            sid for sid in self._sessions.keys()
            if sid not in sessions_to_keep
        ]
        
        for session_id in sessions_to_remove:
            del self._sessions[session_id]
            
    def _export_to_csv(self, session: ValidationSession) -> str:
        """Export session to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Validator",
            "Severity",
            "Category",
            "Message",
            "Element",
            "Location"
        ])
        
        # Write issues
        for result in session.results:
            for issue in result.issues:
                writer.writerow([
                    result.validator_name,
                    issue.severity.value,
                    issue.category,
                    issue.message,
                    issue.element.name if issue.element else "",
                    issue.location or ""
                ])
                
        return output.getvalue()
