import os
import re
import argparse
import sys

def check_file_for_spec_tokens(file_path, patterns, verbose=False):
    issues = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            lines = f.readlines()
    except Exception as e:
        if verbose:
            print(f"Error reading {file_path}: {e}")
        return issues

    for lineno, line in enumerate(lines, start=1):
        for pat in patterns:
            if re.search(pat, line):
                issues.append((lineno, line.strip()))
                if verbose:
                    print(f"  Line {lineno}: {line.strip()}")
    return issues

def check_dir_for_spec_tokens(target_dir, verbose=False):
    spec_patterns = [
        r'\bSPEC\b',
        r'\bSPEC_[A-Z0-9_]+\b'
    ]
    problems = {}
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(('.c', '.cpp', '.h')):
                file_path = os.path.join(root, file)
                file_issues = check_file_for_spec_tokens(file_path, spec_patterns, verbose)
                if file_issues:
                    problems[file_path] = file_issues
                    if verbose:
                        print(f"Modified: {file_path}")
    return problems

def main():
    parser = argparse.ArgumentParser(
        description="Check for leftover SPEC tokens in source files after unspec."
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cpu2017", "benchspec", "CPU"),
        help="Path to benchspec/CPU directory"
    )
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', action='store_true', help='Suppress output except errors')

    args = parser.parse_args()

    if not os.path.isdir(args.target_dir):
        print(f"Invalid directory: {args.target_dir}")
        sys.exit(1)

    problems = check_dir_for_spec_tokens(args.target_dir)

    if problems:
        if not args.quiet:
            print("Leftover SPEC tokens found in the following files:")
            for file_path, issues in problems.items():
                print(f"\nIn file: {file_path}")
                for lineno, line in issues:
                    print(f"  Line {lineno}: {line}")
        sys.exit(1)
    else:
        if args.verbose:
            print("No leftover SPEC tokens found. All files are clean.")
        sys.exit(0)

if __name__ == "__main__":
    main()
