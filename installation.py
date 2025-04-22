import os
import platform
import subprocess
import shutil
import tempfile

def detect_os():
    system = platform.system()
    if system == "Linux":
        return "linux"
    elif system == "Darwin":
        return "mac"
    elif system == "Windows":
        return "windows"
    else:
        raise RuntimeError("Unsupported operating system")

def mount_iso(iso_path, mount_point):
    os_type = detect_os()
    if os_type == "linux":
        subprocess.run(["sudo", "mount", "-o", "loop", iso_path, mount_point], check=True)
    elif os_type == "mac":
        subprocess.run(["hdiutil", "attach", iso_path, "-mountpoint", mount_point], check=True)
    elif os_type == "windows":
        # Requires 7z installed or PowerShell ISO mounting
        subprocess.run(["7z", "x", iso_path, f"-o{mount_point}"], check=True)
    else:
        raise RuntimeError("Unsupported OS for mounting")

def unmount_iso(mount_point):
    os_type = detect_os()
    if os_type == "linux":
        subprocess.run(["sudo", "umount", mount_point], check=True)
    elif os_type == "mac":
        subprocess.run(["hdiutil", "detach", mount_point], check=True)
    elif os_type == "windows":
        # Nothing needed if using 7z
        pass

def run_installer(mount_point, install_dir):
    os_type = detect_os()
    install_script = os.path.join(mount_point, "install.sh")

    if os_type in ["linux", "mac"]:
        install_dir = os.path.abspath(install_dir)

        subprocess.run(
            [install_script, "-d", install_dir, "-f"],
            cwd="/tmp",
            check=True
        )

    elif os_type == "windows":
        install_script = os.path.join(mount_point, "install.bat")
        subprocess.run([install_script, "/D=" + install_dir], shell=True, check=True)


def main(iso_path, output_dir):
    mount_point = tempfile.mkdtemp()
    try:
        print(f"Mounting ISO to {mount_point}")
        mount_iso(iso_path, mount_point)

        print(f"Installing to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        run_installer(mount_point, output_dir)

    finally:
        print("Cleaning up...")
        unmount_iso(mount_point)
        shutil.rmtree(mount_point)

if __name__ == "__main__":
    iso_path = "cpu2017-1_0_5.iso"
    output_dir = "cpu2017"
    main(iso_path, output_dir)
