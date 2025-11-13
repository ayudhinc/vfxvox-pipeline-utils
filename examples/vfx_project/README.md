# VFX Project Example

This example project demonstrates all VFXVox Pipeline Utils tools with realistic VFX production structure.

## Project Structure

```
vfx_project/
├── seq_010/                    # Sequence 010
│   ├── shot_010/              # Shot 010
│   │   ├── plate/             # Original plates
│   │   │   └── shot_010_plate.1001-1100.exr
│   │   ├── comp/              # Compositing
│   │   │   ├── v001/          # Version 001
│   │   │   │   └── shot_010_comp.####.exr
│   │   │   └── v002/          # Version 002 (with issues)
│   │   └── assets/            # Shot-specific assets
│   │       └── prop_table.usd
│   └── shot_020/              # Shot 020
│       ├── plate/
│       ├── comp/
│       │   └── v001/
│       └── assets/
└── assets/                     # Shared assets
    ├── characters/
    │   └── hero_character.usd
    └── environments/
        └── city_street.usd
```

## Test Scenarios

### ShotLint Tests
- ✅ Valid folder structure (seq_010/shot_010)
- ❌ Missing plate folder (seq_010/shot_020)
- ❌ Missing frames in sequence (shot_010/comp/v002)
- ✅ Required files present

### Sequence Validator Tests
- ✅ Complete sequence (shot_010/comp/v001: frames 1001-1100)
- ❌ Missing frames (shot_010/comp/v002: frames 1050-1060 missing)
- ❌ Resolution mismatch (shot_020/comp/v001: mixed resolutions)

### USD Linter Tests
- ✅ Valid USD file (assets/characters/hero_character.usd)
- ❌ Broken references (assets/environments/city_street.usd)
- ❌ Invalid schema (seq_010/shot_010/assets/prop_table.usd)

## Usage Examples

### Validate Directory Structure
```bash
vfxvox shotlint ./vfx_project --rules shotlint_rules.yaml
```

### Validate Image Sequence
```bash
vfxvox validate-sequence "./vfx_project/seq_010/shot_010/comp/v001/shot_010_comp.%04d.exr"
```

### Lint USD Files
```bash
vfxvox lint-usd ./vfx_project/assets/characters/hero_character.usd
```

## Rules Files

- `shotlint_rules.yaml` - Directory structure validation rules
- `shotlint_rules_strict.yaml` - Strict validation with all checks
- `shotlint_rules_minimal.yaml` - Minimal validation for quick checks
