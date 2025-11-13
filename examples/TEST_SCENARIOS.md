# VFXVox Pipeline Utils - Test Scenarios

This document describes test scenarios for all tools in the VFXVox Pipeline Utils toolkit.

## Test Project Structure

The `vfx_project/` directory contains a realistic VFX production structure with intentional issues for testing validation tools.

```
vfx_project/
├── seq_010/
│   ├── shot_010/          # Complete shot with all folders
│   │   ├── plate/         # ✅ Present
│   │   ├── comp/
│   │   │   ├── v001/      # ✅ Complete frames
│   │   │   └── v002/      # ❌ Missing frames 1050-1060
│   │   └── assets/        # ✅ Present
│   └── shot_020/          # Incomplete shot
│       ├── plate/         # ❌ MISSING (test scenario)
│       ├── comp/
│       │   └── v001/      # ❌ Mixed resolutions
│       └── assets/        # ✅ Present
└── assets/
    ├── characters/        # ✅ Valid USD files
    └── environments/      # ❌ Broken USD references
```

## ShotLint Test Scenarios

### Scenario 1: Valid Structure
**Test**: `seq_010/shot_010` with all required folders
**Expected**: ✅ Pass
**Command**:
```bash
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules_minimal.yaml
```

### Scenario 2: Missing Plate Folder
**Test**: `seq_010/shot_020` missing plate folder
**Expected**: ❌ Error - "Plate folders present" rule fails
**Command**:
```bash
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml
```
**Expected Output**:
```
[ERROR] No matches for glob: seq_*/shot_*/plate
```

### Scenario 3: Path Pattern Validation
**Test**: Validate folder naming follows `seq_XXX/shot_XXX` pattern
**Expected**: ✅ Pass for valid folders
**Command**:
```bash
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml
```

### Scenario 4: Frame Sequence Check
**Test**: Check for missing frames in comp sequences
**Expected**: ❌ Error for v002 (missing frames 1050-1060)
**Command**:
```bash
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules_strict.yaml
```
**Expected Output**:
```
[ERROR] Missing frames: [1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060]
    ↳ seq_010/shot_010/comp/v002
```

### Scenario 5: Filename Regex
**Test**: Validate EXR files follow naming convention
**Expected**: ⚠️ Warning if no files match pattern
**Command**:
```bash
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml
```

### Scenario 6: Multiple Output Formats
**Test**: Generate reports in different formats
**Commands**:
```bash
# Console output
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml

# JSON output
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml --format json

# Markdown report
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml --format md --report report.md

# YAML output
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml --format yaml
```

## Sequence Validator Test Scenarios

### Scenario 1: Complete Sequence
**Test**: Validate complete frame sequence (1001-1100)
**Location**: `seq_010/shot_010/comp/v001/`
**Expected**: ✅ Pass - all 100 frames present
**Command**:
```bash
vfxvox validate-sequence "examples/vfx_project/seq_010/shot_010/comp/v001/shot_010_comp.%04d.exr"
```

### Scenario 2: Missing Frames
**Test**: Detect missing frames in sequence
**Location**: `seq_010/shot_010/comp/v002/`
**Expected**: ❌ Error - frames 1050-1060 missing
**Command**:
```bash
vfxvox validate-sequence "examples/vfx_project/seq_010/shot_010/comp/v002/shot_010_comp.%04d.exr"
```
**Expected Output**:
```
[ERROR] Missing frames: [1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059, 1060]
```

### Scenario 3: Resolution Mismatch
**Test**: Detect inconsistent resolution across frames
**Location**: `seq_010/shot_020/comp/v001/`
**Expected**: ❌ Error - mixed resolutions (1920x1080 and 1920x1088)
**Command**:
```bash
vfxvox validate-sequence "examples/vfx_project/seq_010/shot_020/comp/v001/shot_020_comp.%04d.exr"
```
**Expected Output**:
```
[ERROR] Resolution mismatch detected
    Expected: 1920x1080
    Found: 1920x1088 at frame 1050
```

### Scenario 4: Bit Depth Mismatch
**Test**: Detect inconsistent bit depth across frames
**Expected**: ❌ Error - mixed bit depths (16-bit and 32-bit)
**Command**:
```bash
vfxvox validate-sequence "examples/vfx_project/seq_010/shot_020/comp/v001/shot_020_comp.%04d.exr" --check-bit-depth
```

### Scenario 5: Corrupted Files
**Test**: Detect corrupted or unreadable frames
**Expected**: ❌ Error - frame 1075 is corrupted
**Command**:
```bash
vfxvox validate-sequence "examples/vfx_project/seq_010/shot_010/comp/v002/shot_010_comp.%04d.exr"
```

### Scenario 6: Multiple Formats
**Test**: Validate sequences in different formats (EXR, DPX, PNG)
**Commands**:
```bash
# EXR sequence
vfxvox validate-sequence "path/to/sequence.%04d.exr"

# DPX sequence
vfxvox validate-sequence "path/to/sequence.%04d.dpx"

# PNG sequence
vfxvox validate-sequence "path/to/sequence.%04d.png"
```

## USD Linter Test Scenarios

### Scenario 1: Valid USD File
**Test**: Lint a valid USD file with no issues
**Location**: `assets/characters/hero_character.usd`
**Expected**: ✅ Pass - no issues found
**Command**:
```bash
vfxvox lint-usd examples/vfx_project/assets/characters/hero_character.usd
```

### Scenario 2: Broken References
**Test**: Detect broken or missing external references
**Location**: `assets/environments/city_street.usd`
**Expected**: ❌ Error - reference to missing texture file
**Command**:
```bash
vfxvox lint-usd examples/vfx_project/assets/environments/city_street.usd
```
**Expected Output**:
```
[ERROR] Broken reference: ../textures/street_diffuse.png
    ↳ assets/environments/city_street.usd
```

### Scenario 3: Invalid Schema
**Test**: Detect invalid schema definitions
**Location**: `seq_010/shot_010/assets/prop_table.usd`
**Expected**: ❌ Error - invalid schema type
**Command**:
```bash
vfxvox lint-usd examples/vfx_project/seq_010/shot_010/assets/prop_table.usd
```
**Expected Output**:
```
[ERROR] Invalid schema: UnknownPrimType
    ↳ /World/Props/Table
```

### Scenario 4: Performance Issues
**Test**: Detect performance problems (deep layer nesting, large arrays)
**Expected**: ⚠️ Warning - layer depth exceeds recommended limit
**Command**:
```bash
vfxvox lint-usd examples/vfx_project/assets/environments/city_street.usd --check-performance
```
**Expected Output**:
```
[WARNING] Layer composition depth (15) exceeds recommended limit (10)
```

### Scenario 5: Custom Rules
**Test**: Apply studio-specific linting rules
**Expected**: Validation based on custom rules
**Command**:
```bash
vfxvox lint-usd examples/vfx_project/assets/characters/hero_character.usd --config studio_usd_rules.yaml
```

## Integration Test Scenarios

### Scenario 1: Full Project Validation
**Test**: Run all validators on entire project
**Commands**:
```bash
# 1. Validate directory structure
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules.yaml

# 2. Validate all sequences
find examples/vfx_project -name "*.exr" -type f | xargs -I {} vfxvox validate-sequence {}

# 3. Validate all USD files
find examples/vfx_project -name "*.usd" -type f | xargs -I {} vfxvox lint-usd {}
```

### Scenario 2: CI/CD Pipeline Integration
**Test**: Use in automated pipeline with exit codes
**Script**:
```bash
#!/bin/bash
set -e

# Validate structure (fail on error)
vfxvox shotlint ./project --rules rules.yaml --fail-on error

# Validate sequences (fail on error)
vfxvox validate-sequence "./project/seq_*/shot_*/comp/*/*.exr"

# Lint USD files (fail on error)
find ./project -name "*.usd" -exec vfxvox lint-usd {} \;

echo "All validations passed!"
```

### Scenario 3: Pre-Commit Hook
**Test**: Validate changes before commit
**Script** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash

# Get changed files
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

# Validate USD files
for file in $CHANGED_FILES; do
    if [[ $file == *.usd ]]; then
        vfxvox lint-usd "$file" || exit 1
    fi
done

# Validate directory structure if rules changed
if echo "$CHANGED_FILES" | grep -q "shotlint_rules.yaml"; then
    vfxvox shotlint . --rules shotlint_rules.yaml || exit 1
fi
```

### Scenario 4: Batch Validation with Reports
**Test**: Generate comprehensive validation reports
**Script**:
```bash
#!/bin/bash

# Create reports directory
mkdir -p reports

# Structure validation
vfxvox shotlint ./project --rules rules.yaml \
    --format md --report reports/structure_report.md

# Sequence validation
vfxvox validate-sequence "./project/seq_*/shot_*/comp/*/*.exr" \
    --format json > reports/sequence_report.json

# USD validation
find ./project -name "*.usd" -exec vfxvox lint-usd {} \; \
    --format yaml > reports/usd_report.yaml

echo "Reports generated in ./reports/"
```

## Performance Test Scenarios

### Scenario 1: Large Project
**Test**: Validate project with 100+ shots
**Expected**: Complete in reasonable time (<5 minutes)
**Metrics**: Track validation time, memory usage

### Scenario 2: Large Sequence
**Test**: Validate sequence with 10,000+ frames
**Expected**: Efficient scanning without loading all frames
**Metrics**: Memory usage should remain constant

### Scenario 3: Parallel Validation
**Test**: Validate multiple sequences in parallel
**Expected**: Near-linear speedup with multiple cores
**Command**:
```bash
find ./project -name "*.exr" | parallel -j 8 vfxvox validate-sequence {}
```

## Error Recovery Test Scenarios

### Scenario 1: Invalid Rules File
**Test**: Handle malformed YAML gracefully
**Expected**: Clear error message, no crash
**Command**:
```bash
vfxvox shotlint ./project --rules invalid_rules.yaml
```
**Expected Output**:
```
ConfigurationError: Invalid YAML in rules file: ...
```

### Scenario 2: Missing Directory
**Test**: Handle non-existent directory
**Expected**: Clear error message
**Command**:
```bash
vfxvox shotlint ./nonexistent --rules rules.yaml
```
**Expected Output**:
```
FileNotFoundError: Root directory not found: ./nonexistent
```

### Scenario 3: Permission Denied
**Test**: Handle files without read permission
**Expected**: Log error, continue with other files
**Command**:
```bash
chmod 000 ./project/seq_010/shot_010/comp/v001/frame.exr
vfxvox validate-sequence "./project/seq_010/shot_010/comp/v001/*.exr"
```

## Running Tests

### Quick Test
```bash
# Run minimal validation
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules_minimal.yaml
```

### Comprehensive Test
```bash
# Run all validations
vfxvox shotlint examples/vfx_project --rules examples/vfx_project/shotlint_rules_strict.yaml --format md --report test_report.md
```

### Automated Testing
```bash
# Run test suite
pytest tests/

# Run with coverage
pytest --cov=vfxvox_pipeline_utils tests/
```

## Expected Results Summary

| Scenario | Tool | Expected Result |
|----------|------|-----------------|
| Valid structure | ShotLint | ✅ Pass |
| Missing plate folder | ShotLint | ❌ Error |
| Complete sequence | Sequence Validator | ✅ Pass |
| Missing frames | Sequence Validator | ❌ Error |
| Resolution mismatch | Sequence Validator | ❌ Error |
| Valid USD | USD Linter | ✅ Pass |
| Broken references | USD Linter | ❌ Error |
| Invalid schema | USD Linter | ❌ Error |

## Notes

- All test scenarios use the `examples/vfx_project/` directory
- Placeholder files (`.gitkeep`) indicate where actual files would be in production
- Test scenarios are designed to cover common VFX pipeline issues
- Exit codes: 0 = success, 1 = errors found, 2 = warnings only, 3 = validation failed to run
