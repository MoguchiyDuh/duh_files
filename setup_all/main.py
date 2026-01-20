"""
Multi-distro package installer with defensive checking.

Workflow:
1. Detect OS/distro
2. Check all packages (multi-layered detection)
3. Show installation plan
4. Request user approval
5. Execute installation
"""

import argparse
import os
import platform
import sys
from typing import List, Tuple

from arch import ArchInstaller
from base import Colors, DistroInstaller
from checker import DefensiveChecker
from debian import DebianInstaller
from fedora import FedoraInstaller
from macos import MacOSInstaller


def detect_distro() -> DistroInstaller:
    """Detect the current OS/distribution and return appropriate installer."""
    system = platform.system().lower()

    if system == "darwin":
        return MacOSInstaller()
    elif system == "linux":
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                content = f.read().lower()
                if "arch" in content:
                    return ArchInstaller()
                elif "debian" in content or "ubuntu" in content:
                    return DebianInstaller()
                elif "fedora" in content:
                    return FedoraInstaller()

    raise NotImplementedError("Unsupported OS or Distribution")


def check_packages(installer: DistroInstaller) -> Tuple[List[str], List[str]]:
    """
    Check all packages and return lists of installed and missing packages.

    Returns:
        (installed, missing) - Lists of package names
    """
    checker = DefensiveChecker(installer)

    # Silence installer's logger during check phase
    original_log = installer.log
    installer.log = lambda x: None  # type: ignore

    installed = []
    missing = []

    print(f"\n{Colors.CYAN}{'='*100}{Colors.RESET}")
    print(f"{Colors.CYAN}CHECKING PACKAGES{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*100}{Colors.RESET}\n")

    print(f"{'PACKAGE':<30} | {'STATUS':<15} | DETAILS")
    print("-" * 100)

    for name, method, content in installer.PACKAGES:
        is_installed, details = checker.enhanced_check(name, method, content)

        status = "INSTALLED" if is_installed else "MISSING"
        color_code = Colors.GREEN if is_installed else Colors.RED
        details_display = details[:60] + "..." if len(details) > 60 else details

        print(
            f"{name:<30} | {color_code}{status:<15}{Colors.RESET} | {details_display}"
        )

        if is_installed:
            installed.append(name)
        else:
            missing.append(name)

    # Restore logger
    installer.log = original_log

    return installed, missing


def print_summary(installed: List[str], missing: List[str]) -> None:
    """Print summary of check results."""
    total = len(installed) + len(missing)
    pct = (len(installed) * 100 // total) if total > 0 else 0

    print("-" * 100)
    print(f"\n{Colors.CYAN}📊 SUMMARY{Colors.RESET}")
    print(
        f"  {Colors.GREEN}✓ Installed:{Colors.RESET} {len(installed)}/{total} ({pct}%)"
    )
    print(
        f"  {Colors.RED}✗ Missing:{Colors.RESET}   {len(missing)}/{total} ({100-pct}%)"
    )


def request_approval(missing: List[str], auto_yes: bool = False) -> bool:
    """
    Request user approval to install missing packages.

    Args:
        missing: List of missing package names
        auto_yes: Auto-approve without prompting

    Returns:
        True if user approved, False otherwise
    """
    if not missing:
        print(f"\n{Colors.GREEN}✓ All packages are already installed!{Colors.RESET}")
        return False

    print(f"\n{Colors.YELLOW}Missing packages ({len(missing)}):{Colors.RESET}")
    for pkg in missing:
        print(f"  - {pkg}")

    # Auto-approve if --yes flag
    if auto_yes:
        print(f"\n{Colors.CYAN}Auto-approved via --yes flag{Colors.RESET}")
        return True

    # Interactive prompt
    print(f"\n{Colors.CYAN}Proceed with installation?{Colors.RESET}")
    try:
        response = input(f"[y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False

    return response == "y"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Multi-distro package installer with defensive checking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py                # Check packages, ask for approval, install
  python3 main.py --dry-run      # Check packages only (no installation)
  python3 main.py --yes          # Auto-approve and install without prompt
  python3 main.py -y --dry-run   # Check packages only (--dry-run overrides --yes)
        """,
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Auto-approve installation without prompting",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Check packages only, do not install anything",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output from package managers",
    )
    parser.add_argument(
        "--hyprland",
        action="store_true",
        help="Install Hyprland ecosystem and desktop tools (Arch only)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    try:
        # Step 1: Detect OS/distro
        print(f"{Colors.CYAN}🔍 Detecting system...{Colors.RESET}")
        installer = detect_distro()
        installer.verbose = args.verbose
        if hasattr(installer, "hyprland"):
            setattr(installer, "hyprland", args.hyprland)
        print(f"Detected: {Colors.GREEN}{installer.log_id.upper()}{Colors.RESET}")

        # Step 2: Check all packages
        installed, missing = check_packages(installer)

        # Step 3: Show summary
        print_summary(installed, missing)

        # Dry-run mode: exit after showing results
        if args.dry_run:
            if missing:
                print(
                    f"\n{Colors.CYAN}Dry-run mode: No installation performed.{Colors.RESET}"
                )
                print(f"To install, run: {Colors.GREEN}python3 main.py{Colors.RESET}")
            sys.exit(0)

        # Step 4: Request approval
        if not request_approval(missing, auto_yes=args.yes):
            print(f"\n{Colors.YELLOW}Installation aborted.{Colors.RESET}")
            sys.exit(0)

        # Step 5: Execute installation
        print(f"\n{Colors.CYAN}{'='*100}{Colors.RESET}")
        print(f"{Colors.CYAN}STARTING INSTALLATION{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*100}{Colors.RESET}\n")

        installer.check_update()
        installer.install_all()

        print(f"\n{Colors.GREEN}{'='*100}{Colors.RESET}")
        print(f"{Colors.GREEN}✓ INSTALLATION COMPLETE{Colors.RESET}")
        print(f"{Colors.GREEN}{'='*100}{Colors.RESET}\n")

    except NotImplementedError:
        print(f"{Colors.RED}Error: Unsupported OS or Distribution{Colors.RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Operation cancelled by user.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
