import os
import re
import argparse
import sys

def check_file_for_spec_tokens(file_path, patterns):
    """
    Check a single file for any occurrence of patterns that indicate leftover SPEC tokens.
    
    Returns a list of tuples (line_number, line_text) for each match.
    """
    issues = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return issues

    for lineno, line in enumerate(lines, start=1):
        for pat in patterns:
            if re.search(pat, line):
                issues.append((lineno, line.strip()))
    return issues

def check_dir_for_spec_tokens(target_dir):
    """
    Walk through target_dir recursively and check all source files for leftover SPEC tokens.
    
    Returns a dictionary mapping file paths to lists of (line number, offending line).
    """
    spec_patterns = [
        r'\bSPEC\b',             # Standalone token SPEC
        r'\bSPEC_[A-Z0-9_]+\b'    # Tokens starting with SPEC_
    ]
    problems = {}
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.c', '.cpp', '.h')):
                file_path = os.path.join(root, file)
                file_issues = check_file_for_spec_tokens(file_path, spec_patterns)
                if file_issues:
                    problems[file_path] = file_issues
    return problems

def main():
    parser = argparse.ArgumentParser(
        description="Check for leftover SPEC tokens in source files after unspec."
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cpu2017", "benchspec", "CPU"),
        help="Path to benchspec/CPU directory (default: ./cpu2017/benchspec/CPU relative to the script)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.target_dir):
        print(f"Invalid directory: {args.target_dir}")
        sys.exit(1)

    problems = check_dir_for_spec_tokens(args.target_dir)
    if problems:
        print("Leftover SPEC tokens found in the following files:")
        for file_path, issues in problems.items():
            print(f"\nIn file: {file_path}")
            for lineno, line in issues:
                print(f"  Line {lineno}: {line}")
        sys.exit(1)
    else:
        print("No leftover SPEC tokens found. All files are clean.")
        sys.exit(0)

if __name__ == "__main__":
    main()
