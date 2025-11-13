# ShotLint - Directory Structure Validator

ShotLint is a rule-based directory structure validator for VFX production pipelines. It validates folder hierarchies, naming conventions, frame sequences, and file presence using declarative YAML rules.

## Features

- **Path Pattern Validation**: Validate folder structures match expected hierarchies
- **Filename Regex Validation**: Ensure files follow naming conventions
- **Frame Sequence Validation**: Check for missing frames in image sequences
- **File Presence Validation**: Verify required files and folders exist
- **Plugin System**: Extend with custom Python validators
- **Multiple Output Formats**: Console, JSON, YAML, and Markdown reports

## Quick Start

### Python API

```python
from vfxvox_pipeline_utils.shotlint import ShotLintValidator
from pathlib import Path

# Create validator
validator = ShotLintValidator()

# Validate directory
result = validator.validate(
    root=Path("./project"),
    rules_path=Path("./rules.yaml")
)

# Check results
if result.has_errors():
    print(f"Found {result.error_count()} errors")
    for error in result.get_errors():
        print(f"  - {error.message}")
```

### CLI

```bash
# Validate with default output
vfxvox shotlint ./project --rules rules.yaml

# JSON output
vfxvox shotlint ./project --rules rules.yaml --format json

# Markdown report
vfxvox shotlint ./project --rules rules.yaml --format md --report report.md
```

## Rule Types

### 1. Path Pattern

Validates folder structure matches expected hierarchy with variable substitution.

```yaml
- name: "Shot structure"
  type: "path_pattern"
  pattern: "seq_{sequence}/shot_{shot}/comp/v{version}"
  vars:
    sequence: "\\d{3}"
    shot: "\\d{3}"
    version: "v\\d{3}"
```

**Variables**: Use `{variable_name}` in pattern, define regex in `vars`

**Example matches**:
- `seq_010/shot_020/comp/v001` ✅
- `seq_100/shot_050/comp/v010` ✅
- `seq_01/shot_020/comp/v001` ❌ (sequence must be 3 digits)

### 2. Filename Regex

Validates filenames match regex patterns.

```yaml
- name: "EXR naming"
  type: "filename_regex"
  regex: "^shot_\\d{3}_v\\d{3}_comp\\.exr$"
```

**Searches**: Recursively through all files in directory tree

**Example matches**:
- `shot_010_v001_comp.exr` ✅
- `shot_020_v010_comp.exr` ✅
- `shot_10_v1_comp.exr` ❌ (wrong padding)

### 3. Frame Sequence

Checks for missing frames in image sequences.

```yaml
- name: "Comp frames"
  type: "frame_sequence"
  folder: "seq_010/shot_020/comp/v001"
  base: "shot_020_v001_comp"
  ext: ".exr"
  start: 1001
  end: 1100
  padding: 4
```

**Fields**:
- `folder`: Relative path from root
- `base`: Filename base (before frame number)
- `ext`: File extension (default: `.exr`)
- `start`: First frame number
- `end`: Last frame number
- `padding`: Frame number padding (default: 4)

**Expected format**: `{base}.{frame}.{ext}`
- Example: `shot_020_v001_comp.1001.exr`

### 4. Must Exist

Verifies required files/folders exist using glob patterns.

```yaml
- name: "Plate files"
  type: "must_exist"
  glob: "seq_*/shot_*/plate/*_plate.*"
```

**Glob patterns**:
- `*`: Matches any characters
- `**`: Matches directories recursively
- `?`: Matches single character
- `[abc]`: Matches any character in brackets

**Examples**:
- `seq_*/shot_*` - All shot folders
- `**/comp/**/*.exr` - All EXR files in comp folders
- `assets/**/*.usd` - All USD files in assets

### 5. Plugin

Execute custom Python validators.

```yaml
- name: "Custom metadata check"
  type: "plugin"
  module: "my_studio.validators:check_metadata"
  options:
    required_fields: ["artist", "date"]
```

**Plugin function signature**:

```python
def validate(context: dict) -> List[dict]:
    """
    Args:
        context: {
            'root': Path,      # Root directory
            'options': dict    # Options from rule
        }
    
    Returns:
        List of issue dicts:
        [
            {
                'level': 'error',      # or 'warning', 'info'
                'message': 'Issue description',
                'path': '/path/to/file',  # optional
                'rule': 'Rule name'       # optional
            }
        ]
    """
    root = context["root"]
    options = context["options"]
    
    issues = []
    # Your validation logic here
    return issues
```

## Configuration

### Rule File Structure

```yaml
rules:
  - name: "Rule name"
    type: "rule_type"
    # ... rule-specific fields
```

**Required fields**:
- `name`: Human-readable rule name
- `type`: Rule type (path_pattern, filename_regex, frame_sequence, must_exist, plugin)

### Severity Levels

- **error**: Critical issues that must be fixed
- **warning**: Issues that should be reviewed
- **info**: Informational messages

Rules automatically assign severity:
- `path_pattern`: warning (if no match)
- `filename_regex`: warning (if no match)
- `frame_sequence`: error (if frames missing)
- `must_exist`: error (if files missing)
- `plugin`: determined by plugin

## Output Formats

### Console (default)

```
ShotLint — ./project
Rules: 5  Errors: 2  Warnings: 1

[ERROR] Missing frames: [1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060]
    ↳ seq_010/shot_010/comp/v002
      missing_count: 11
      expected_range: 1001-1100

[WARNING] No path matched pattern 'seq_{sequence}/shot_{shot}/plate'
    ↳ ./project
```

### JSON

```json
{
  "passed": false,
  "issues": [
    {
      "severity": "error",
      "message": "Missing frames: [1050, 1051, ...]",
      "location": "seq_010/shot_010/comp/v002",
      "details": {
        "missing_count": 11,
        "expected_range": "1001-1100"
      }
    }
  ],
  "metadata": {
    "validator": "ShotLintValidator",
    "root": "./project",
    "rule_count": 5
  },
  "summary": {
    "total_issues": 3,
    "errors": 2,
    "warnings": 1,
    "info": 0
  }
}
```

### Markdown

```markdown
# ShotLint Report for `./project`

- **Rules**: 5
- **Errors**: 2
- **Warnings**: 1

## Errors

- **Missing frames: [1050, 1051, ...]**
  - Location: `seq_010/shot_010/comp/v002`
  - missing_count: `11`
  - expected_range: `1001-1100`

## Warnings

- **No path matched pattern 'seq_{sequence}/shot_{shot}/plate'**
  - Location: `./project`
```

## Best Practices

### 1. Start Simple

Begin with basic structure validation:

```yaml
rules:
  - name: "Shot folders exist"
    type: "must_exist"
    glob: "seq_*/shot_*"
```

### 2. Layer Validation

Add more specific rules progressively:

```yaml
rules:
  # Level 1: Basic structure
  - name: "Shot folders"
    type: "must_exist"
    glob: "seq_*/shot_*"
  
  # Level 2: Folder hierarchy
  - name: "Shot structure"
    type: "path_pattern"
    pattern: "seq_{sequence}/shot_{shot}"
    vars:
      sequence: "\\d{3}"
      shot: "\\d{3}"
  
  # Level 3: File presence
  - name: "Comp folders"
    type: "must_exist"
    glob: "seq_*/shot_*/comp"
  
  # Level 4: Frame sequences
  - name: "Comp frames"
    type: "frame_sequence"
    folder: "seq_010/shot_010/comp/v001"
    base: "shot_010_comp"
    ext: ".exr"
    start: 1001
    end: 1100
```

### 3. Use Descriptive Names

Make rule names clear and actionable:

```yaml
# Good
- name: "Shot 010 comp v001 has all frames (1001-1100)"
  type: "frame_sequence"
  # ...

# Less clear
- name: "Frames check"
  type: "frame_sequence"
  # ...
```

### 4. Document Your Rules

Add comments to explain complex patterns:

```yaml
rules:
  # Validates standard shot structure: seq_XXX/shot_XXX/dept/vXXX
  # Where XXX is a 3-digit number
  - name: "Shot folder structure"
    type: "path_pattern"
    pattern: "seq_{sequence}/shot_{shot}/{dept}/v{version}"
    vars:
      sequence: "\\d{3}"
      shot: "\\d{3}"
      dept: "(comp|plate|assets)"
      version: "\\d{3}"
```

### 5. Test Rules Incrementally

Test each rule individually before combining:

```bash
# Test single rule
vfxvox shotlint ./project --rules test_rule.yaml

# Add to main rules once validated
cat test_rule.yaml >> main_rules.yaml
```

## Error Handling

### Common Issues

**1. YAML Syntax Errors**

```
ConfigurationError: Invalid YAML in rules file
```

**Solution**: Validate YAML syntax, check indentation and quotes

**2. Invalid Regex**

```
ValidationIssue: Invalid regex pattern
```

**Solution**: Test regex patterns, escape special characters properly

**3. Plugin Import Errors**

```
ValidationIssue: Failed to load plugin: No module named 'my_module'
```

**Solution**: Ensure plugin module is in Python path

### Debugging

Enable debug logging:

```python
from vfxvox_pipeline_utils.core import setup_logging

setup_logging(level="DEBUG")
```

Or via CLI:

```bash
vfxvox --log-level DEBUG shotlint ./project --rules rules.yaml
```

## Examples

See `examples/vfx_project/` for complete examples:

- `shotlint_rules.yaml` - Standard validation
- `shotlint_rules_strict.yaml` - Comprehensive validation
- `shotlint_rules_minimal.yaml` - Quick checks

## API Reference

### ShotLintValidator

```python
class ShotLintValidator(BaseValidator):
    def validate(self, root: Path, rules_path: Path) -> ValidationResult:
        """Validate directory structure against rules."""
    
    def load_rules(self, rules_path: Path) -> List[Dict[str, Any]]:
        """Load validation rules from YAML file."""
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    passed: bool
    issues: List[ValidationIssue]
    metadata: dict
    
    def has_errors(self) -> bool
    def has_warnings(self) -> bool
    def error_count(self) -> int
    def warning_count(self) -> int
    def get_errors(self) -> List[ValidationIssue]
    def get_warnings(self) -> List[ValidationIssue]
```

### ValidationIssue

```python
@dataclass
class ValidationIssue:
    severity: str  # 'error', 'warning', 'info'
    message: str
    location: Optional[str]
    details: Optional[dict]
```

## Contributing

To add new rule types:

1. Create rule class in `rules.py`
2. Implement `check(root, rule)` method
3. Register in `engine.py` dispatch table
4. Add tests and documentation

See `CONTRIBUTING.md` for details.
