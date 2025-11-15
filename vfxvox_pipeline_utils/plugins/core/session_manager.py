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
    """Manages validation sessions and persistence."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize session manager with optional storage path."""
        self._storage_path = storage_path or self._get_default_storage_path()
        self._current_session: Optional[ValidationSession] = None
        self._sessions: Dict[str, ValidationSession] = {}
        
    def create_session(
        self,
        context: ValidationContext
    ) -> ValidationSession:
        """Create a new validation session."""
        import uuid
        
        session = ValidationSession(
            session_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            context=context,
            results=[]
        )
        
        self._current_session = session
        self._sessions[session.session_id] = session
        
        return session
        
    def add_result(
        self,
        session_id: str,
        result: ValidationResult
    ) -> None:
        """Add a validation result to a session."""
        if session_id in self._sessions:
            self._sessions[session_id].results.append(result)
            self._persist_session(self._sessions[session_id])
            
    def get_session(self, session_id: str) -> Optional[ValidationSession]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
        
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
            
    def _get_default_storage_path(self) -> str:
        """Get default storage path for sessions."""
        import os
        from pathlib import Path
        
        home = Path.home()
        storage_path = home / ".vfxvox" / "sessions"
        storage_path.mkdir(parents=True, exist_ok=True)
        
        return str(storage_path)
        
    def _persist_session(self, session: ValidationSession) -> None:
        """Persist session to disk."""
        import json
        from dataclasses import asdict
        from pathlib import Path
        
        storage_path = Path(self._storage_path)
        session_file = storage_path / f"{session.session_id}.json"
        
        with open(session_file, "w") as f:
            json.dump(asdict(session), f, indent=2, default=str)
            
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
