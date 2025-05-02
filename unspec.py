import os
import argparse
import shutil
import sys
import subprocess
import re

def remove_makefiles(target_dir):
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file == "Makefile":
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

def copy_makefile(target_dir):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_makefile = os.path.join(script_dir, 'Makefile')
    target_makefile = os.path.join(target_dir, 'Makefile')

    if not os.path.exists(source_makefile):
        print(f"Makefile not found in {script_dir}")
        return

    try:
        shutil.copy(source_makefile, target_makefile)
    except Exception as e:
        print(f"Error copying Makefile: {e}")

def check_for_main(folder):
    main_pattern = re.compile(r'int\s+main\s*\(.*?\)')
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(('.c', '.cpp')):
                try:
                    with open(os.path.join(root, file), "r", errors="ignore") as f:
                        if main_pattern.search(f.read()):
                            return True
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    return False

def run_makefile(target_dir):
    if not os.path.exists(target_dir):
        print(f"Missing directory: {target_dir}")
        return

    makefile_path = os.path.join(target_dir, 'Makefile')
    if not os.path.exists(makefile_path):
        print(f"Makefile missing in {target_dir}")
        return

    try:
        result = subprocess.run(['make'], cwd=target_dir,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        if result.returncode == 0:
            print("Build successful!")
            print(result.stdout)
        else:
            print("Build failed!")
            print(result.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Make error: {e}")
        sys.exit(1)

def replace_line(file_path, old_line, new_line):
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    replaced = False
    for i, line in enumerate(lines):
        if old_line in line:
            lines[i] = new_line + "\n"
            replaced = True

    if replaced:
        try:
            with open(file_path, 'w', errors='ignore') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

def remove_if(file_path, start_line, remove_else=True):
    """Removes a block starting with a fixed start_line until the matching '#endif'."""
    end_marker = "#endif"
    else_marker = "#else"

    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    new_lines = []
    in_block = False
    in_else = False

    for line in lines:
        if start_line in line:
            in_block = True
            continue
        if in_block and end_marker in line:
            in_block = False
            in_else = False
            continue
        if in_block and else_marker in line:
            in_else = True
            continue
        if not in_block or (in_else and not remove_else) or (not in_else and remove_else):
            new_lines.append(line)
    if new_lines != lines:
        try:
            with open(file_path, 'w', errors='ignore') as f:
                f.writelines(new_lines)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

def remove_if_regex(file_path, pattern, remove_else=True):
    """Removes a block starting with any line matching the regex until the matching '#endif'."""
    end_marker = "#endif"
    else_marker = "#else"
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    new_lines = []
    in_block = False
    in_else = False

    for line in lines:
        if re.search(pattern, line):
            in_block = True
            continue
        if in_block and end_marker in line:
            in_block = False
            in_else = False
            continue
        if in_block and else_marker in line:
            in_else = True
            continue
        if not in_block or (in_else and not remove_else) or (not in_else and remove_else):
            new_lines.append(line)
    if new_lines != lines:
        try:
            with open(file_path, 'w', errors='ignore') as f:
                f.writelines(new_lines)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

def remove_spec_tokens(file_path):
    """
    Remove any leftover tokens that reference SPEC.
    Removes whole-word "SPEC" and tokens starting with "SPEC_".
    """
    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    original = content
    content = re.sub(r'\bSPEC\b', '', content)
    content = re.sub(r'\bSPEC_[A-Z0-9_]+\b', '', content)

    if content != original:
        try:
            with open(file_path, 'w', errors='ignore') as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing {file_path}: {e}")

def unspec_file(file_path):
    # Fix OpenMP detection line
    replace_line(
        file_path,
        "#if (defined(_OPENMP) || defined(SPEC_OPENMP)) && !defined(SPEC_SUPPRESS_OPENMP) && !defined(SPEC_AUTO_SUPPRESS_OPENMP)",
        "#if defined(_OPENMP)"
    )

    # Remove blocks with fixed conditionals
    conditions_fixed = [
        ("#ifdef SPEC", False),
        ("#if defined(SPEC)", False),
        ("#ifndef SPEC", True),
        ("#if !defined(SPEC)", True),
        ("#ifdef SPEC_MPI", True),
        ("#if defined(SPEC_MPI)", True)
    ]
    for start_line, remove_else in conditions_fixed:
        remove_if(file_path, start_line, remove_else)
    
    # Remove blocks that contain SPEC in more complex conditionals via regex.
    regex_conditions = [
        r'^#if\s+.*\bSPEC\b.*$'
    ]
    for pattern in regex_conditions:
        remove_if_regex(file_path, pattern, remove_else=True)
    
    # Remove any stray SPEC tokens.
    remove_spec_tokens(file_path)

def unspec_folder(folder_path, verbose):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.c', '.h', '.cpp')):
                unspec_file(os.path.join(root, file))

def main():
    parser = argparse.ArgumentParser(
        description="Unspec and build SPEC benchmarks from cpu2017/benchspec/CPU"
    )
    parser.add_argument("--benchspec", 
                        help="Path to benchspec/CPU directory (default: ./cpu2017/benchspec/CPU relative to script)",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cpu2017", "benchspec", "CPU"))
    args = parser.parse_args()

    benchspec_cpu = args.benchspec
    if not os.path.isdir(benchspec_cpu):
        print(f"Invalid benchspec/CPU directory: {benchspec_cpu}")
        sys.exit(1)

    # Look for directories named "src" or starting with "build_base_"
    target_dirs = []
    for root, dirs, _ in os.walk(benchspec_cpu):
        for d in dirs:
            if d == "src" or d.startswith("build_base_"):
                target_dirs.append(os.path.join(root, d))

    if not target_dirs:
        print("No target directories found.")
        sys.exit(1)

    print(f"Found {len(target_dirs)} target directories.\n")
    for t_dir in target_dirs:
        print(f"Processing directory: {t_dir}")
        print("Removing existing Makefiles...")
        remove_makefiles(t_dir)
        print("Copying new Makefile...")
        copy_makefile(t_dir)
        print("Removing SPEC conditionals and tokens...")
        unspec_folder(t_dir)
        print("Checking for main()...")
        if not check_for_main(t_dir):
            print(f"WARNING: No main() function found in {t_dir}. Skipping build.\n")
            continue
        print("Building...")
        run_makefile(t_dir)
        print("\n----------------------------------------\n")

if __name__ == "__main__":
    main()
