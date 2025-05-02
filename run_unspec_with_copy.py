#!/usr/bin/env python3
import os
import shutil
import argparse
import subprocess
import sys

# Import unspec functions
from unspec import remove_makefiles, copy_makefile, unspec_folder


def find_target_dirs(root):
    """
    Find all subdirectories named 'src' or starting with 'build_base_' under root.
    """
    targets = []
    for base, dirs, _ in os.walk(root):
        for d in dirs:
            if d == "src" or d.startswith("build_base_"):
                targets.append(os.path.join(base, d))
    return targets


def process_benchmark(bench_dir, out_dir):
    bench_name = os.path.basename(bench_dir.rstrip(os.sep))
    work_dir = os.path.join(out_dir, bench_name)

    # Copy benchmark to workspace
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    shutil.copytree(bench_dir, work_dir)
    print(f"Copied benchmark {bench_name} to {work_dir}")

    # Apply unspec transformations
    target_dirs = find_target_dirs(work_dir)
    if not target_dirs:
        print(f"No target directories found in {bench_name}. Marking as FAIL.")
        return False
    for tdir in target_dirs:
        print(f"\n--- Unspeç directory: {tdir} ---")
        remove_makefiles(tdir)
        copy_makefile(tdir)
        unspec_folder(tdir)

    # Run check-unspec
    script_dir = os.path.dirname(os.path.abspath(__file__))
    check_script = os.path.join(script_dir, 'check_unspec.py')
    print(f"Running check-unspec on {work_dir}")
    result = subprocess.run(
        [sys.executable, check_script, work_dir],
        cwd=script_dir
    )
    if result.returncode == 0:
        print(f"check-unspec PASSED for {bench_name}")
        return True
    else:
        print(f"check-unspec FAILED for {bench_name}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Copy each SPEC CPU2017 benchmark, apply unspec, then run check-unspec"
    )
    parser.add_argument(
        '--benchspec',
        default=os.path.join(os.path.dirname(__file__), 'cpu2017', 'benchspec', 'CPU'),
        help='Path to benchspec/CPU directory'
    )
    parser.add_argument(
        '--output',
        default='spec2017-unspec',
        help='Output base directory for unspecced benchmarks'
    )
    parser.add_argument(
        '--benchmark',
        default=None,
        help="Optional single benchmark name to process, e.g. '500.s'"
    )
    args = parser.parse_args()

    benchspec_cpu = os.path.abspath(args.benchspec)
    out_dir = os.path.abspath(args.output)
    pass_dir = os.path.join(out_dir, 'pass')
    fail_dir = os.path.join(out_dir, 'fail')
    os.makedirs(pass_dir, exist_ok=True)
    os.makedirs(fail_dir, exist_ok=True)

    # Process each benchmark
    for bench_name in sorted(os.listdir(benchspec_cpu)):
        if args.benchmark and bench_name != args.benchmark:
            continue
        bench_dir = os.path.join(benchspec_cpu, bench_name)
        if not os.path.isdir(bench_dir):
            continue

        success = process_benchmark(bench_dir, out_dir)

        # Move to final pass/fail directory
        src = os.path.join(out_dir, bench_name)
        dest_base = pass_dir if success else fail_dir
        dest = os.path.join(dest_base, bench_name)
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.move(src, dest)
        print(f"Moved {bench_name} to {dest_base} ({'PASS' if success else 'FAIL'})")


if __name__ == '__main__':
    main()
