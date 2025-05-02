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


def find_7z():
    # Try locating 7z in PATH
    for cmd in ("7z", "7z.exe"):
        path = shutil.which(cmd)
        if path:
            return path
    # Check common installation directories
    possible_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe"
    ]
    for p in possible_paths:
        if os.path.isfile(p):
            return p
    raise RuntimeError("7-Zip executable not found. Please install 7-Zip or add it to your PATH.")


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

def main(iso_path, output_dir):
    os_type = detect_os()
    

    if os_type == "windows":
        iso_path = os.path.abspath(iso_path)
        output_dir = os.path.abspath(output_dir) if output_dir else None
        output_dir = output_dir or os.path.splitext(iso_path)[0] + '_extr'
        print(f"Extracting ISO to {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        seven_z = find_7z()
        subprocess.run([seven_z, "x", iso_path, f"-o{output_dir}"], check=True)
        print("Extraction complete.")

        # Detect nested folder
        entries = os.listdir(output_dir)
        if len(entries) == 1 and os.path.isdir(os.path.join(output_dir, entries[0])):
            source_dir = os.path.join(output_dir, entries[0])
        else:
            source_dir = output_dir

        print(f"Running installer in {source_dir}")
        installer = os.path.join(source_dir, "install.bat")
        # Execute batch installer directly; it will install to assumed location
        subprocess.run(installer, shell=True, cwd=source_dir, check=True)
        print("Installation complete.")
        
    elif os_type == "linux" or os_type == "mac":
        # Linux/macOS flow: mount and install with explicit output_dir
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

