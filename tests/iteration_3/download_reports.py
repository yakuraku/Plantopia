"""
Download test reports from GCP VM to local PC
Run this on your LOCAL machine after tests complete on VM
"""

import subprocess
import os
import sys
from datetime import datetime


def download_reports_from_vm():
    """Download test reports from GCP VM via SCP"""

    print("\n" + "="*70)
    print("DOWNLOAD TEST REPORTS FROM GCP VM")
    print("="*70 + "\n")

    # Get VM details from environment or prompt
    vm_ip = os.environ.get('GCP_VM_IP')
    vm_user = os.environ.get('GCP_VM_USER', 'ubuntu')

    if not vm_ip:
        print("Enter your GCP VM IP address:")
        vm_ip = input("GCP VM IP: ").strip()

    if not vm_ip:
        print("❌ Error: VM IP address is required")
        return 1

    # Paths
    remote_reports_dir = "/opt/plantopia/Plantopia/tests/iteration_3/reports"
    local_reports_dir = os.path.join(os.path.dirname(__file__), "reports")

    # Create local reports directory if it doesn't exist
    os.makedirs(local_reports_dir, exist_ok=True)

    print(f"📡 Connecting to VM: {vm_user}@{vm_ip}")
    print(f"📥 Downloading from: {remote_reports_dir}")
    print(f"📁 Saving to: {local_reports_dir}")
    print()

    # Build SCP command to download all reports
    scp_command = [
        "scp",
        "-r",  # Recursive
        f"{vm_user}@{vm_ip}:{remote_reports_dir}/*",
        local_reports_dir
    ]

    try:
        print("⏳ Downloading reports...")
        result = subprocess.run(
            scp_command,
            check=True,
            capture_output=True,
            text=True
        )

        print("✅ Reports downloaded successfully!")
        print()

        # List downloaded files
        print("📊 Downloaded reports:")
        for filename in sorted(os.listdir(local_reports_dir)):
            if filename.endswith(('.json', '.txt')):
                filepath = os.path.join(local_reports_dir, filename)
                size = os.path.getsize(filepath)
                print(f"   - {filename} ({size:,} bytes)")

        print()
        print("💡 View reports:")
        print(f"   cd {local_reports_dir}")
        print(f"   # Then open .json or .txt files in your editor")
        print()

        # Find and display latest summary
        summary_files = [f for f in os.listdir(local_reports_dir) if f.startswith('summary_') and f.endswith('.txt')]
        if summary_files:
            latest_summary = sorted(summary_files)[-1]
            summary_path = os.path.join(local_reports_dir, latest_summary)

            print("="*70)
            print("LATEST TEST SUMMARY")
            print("="*70)
            with open(summary_path, 'r') as f:
                print(f.read())

        return 0

    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading reports: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify VM IP and user are correct")
        print("2. Ensure you have SSH access to the VM")
        print("3. Check that tests have been run on the VM")
        print("4. Verify reports directory exists on VM")
        print()
        print("Manual download command:")
        print(f"   scp -r {vm_user}@{vm_ip}:{remote_reports_dir}/* {local_reports_dir}")
        return 1

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


def main():
    """Main entry point"""

    # Check if running on Windows (needs different approach)
    if sys.platform == "win32":
        print("⚠️  Note: On Windows, you may need:")
        print("   - Git Bash, WSL, or PuTTY's pscp")
        print("   - Or use WinSCP GUI application")
        print()

        # Try to detect Git Bash
        git_bash = os.path.exists("C:\\Program Files\\Git\\bin\\bash.exe")
        if git_bash:
            print("✅ Git Bash detected. This script should work.")
        else:
            print("💡 Alternative: Use WinSCP or similar tool to download:")
            print(f"   Remote path: /opt/plantopia/Plantopia/tests/iteration_3/reports/")
            print(f"   Local path: {os.path.join(os.path.dirname(__file__), 'reports')}")
            print()

    exit_code = download_reports_from_vm()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
