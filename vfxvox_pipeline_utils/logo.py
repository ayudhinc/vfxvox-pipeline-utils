"""ASCII logo for VFXVox Pipeline Utils."""

# Full logo for README and documentation
LOGO_FULL = r"""
 ██╗   ██╗███████╗██╗  ██╗██╗   ██╗ ██████╗ ██╗  ██╗
 ██║   ██║██╔════╝╚██╗██╔╝██║   ██║██╔═══██╗╚██╗██╔╝
 ██║   ██║█████╗   ╚███╔╝ ██║   ██║██║   ██║ ╚███╔╝ 
 ╚██╗ ██╔╝██╔══╝   ██╔██╗ ╚██╗ ██╔╝██║   ██║ ██╔██╗ 
  ╚████╔╝ ██║     ██╔╝ ██╗ ╚████╔╝ ╚██████╔╝██╔╝ ██╗
   ╚═══╝  ╚═╝     ╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚═╝  ╚═╝
                                                       
Pipeline Utils v{version} - VFX Validation Toolkit       
"""

# Compact logo for CLI
LOGO_CLI = r"""
╔══════════════════════════════════════════════════════╗
║                                                      ║
║  ██╗   ██╗███████╗██╗  ██╗██╗   ██╗ ██████╗ ██╗  ██╗ ║
║  ██║   ██║██╔════╝╚██╗██╔╝██║   ██║██╔═══██╗╚██╗██╔╝ ║
║  ╚██╗ ██╔╝█████╗   ╚███╔╝ ╚██╗ ██╔╝██║   ██║ ╚███╔╝  ║
║   ╚████╔╝ ██╔══╝   ██╔██╗  ╚████╔╝ ██║   ██║ ██╔██╗  ║
║    ╚═══╝  ██║     ██╔╝ ██╗  ╚═══╝  ╚██████╔╝██╔╝ ██╗ ║
║           ╚═╝     ╚═╝  ╚═╝          ╚═════╝ ╚═╝  ╚═╝ ║
║                                                      ║
║           Pipeline Utils v{version}                  ║
║           VFX Validation Toolkit                     ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""

# Minimal banner for CLI
LOGO_MINIMAL = """
┌─────────────────────────────────────────┐
│  VFXVox Pipeline Utils v{version}       │
│  VFX Validation Toolkit                 │
└─────────────────────────────────────────┘
"""


def get_logo(style: str = "full", version: str = "") -> str:
    """Get ASCII logo.

    Args:
        style: Logo style ('full', 'cli', 'minimal')
        version: Version string to include in logo

    Returns:
        ASCII logo string
    """
    if style == "cli":
        return LOGO_CLI.format(version=version)
    elif style == "minimal":
        return LOGO_MINIMAL.format(version=version)
    else:
        return LOGO_FULL.format(version=version)


def print_logo(style: str = "full", version: str = "") -> None:
    """Print ASCII logo to console.

    Args:
        style: Logo style ('full', 'cli', 'minimal')
        version: Version string to include in logo
    """
    print(get_logo(style, version))
