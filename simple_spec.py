#!/usr/bin/env python3
"""
Simple SPEC

This script automatically processes multiple CPU2017 benchmarks using existing
cleaner scripts and makefiles.

Directory structure expected:
program_dir/
├── libs/
│   ├── lbm/
│   │   ├── cleaner.py
│   │   └── Makefile
│   ├── mcf/
│   │   ├── cleaner.py
│   │   └── Makefile│
|   ├── namd/
│   │   ├── apoa1.input
│   │   ├── cleaner.py
│   │   └── Makefile
│   └── deepsjeng/
│       ├── cleaner.py
│       └── Makefile
└── simple_spec.py (this script)

Usage:
    python3 simple_spec.py [options]
    python3 simple_spec.py --cpu2017-dir "/path/to/cpu2017"
    python3 simple_spec.py --output-dir "/path/to/cleaned_benchmarks"
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SimpleSpec:
    def __init__(self, cpu2017_dir: Path, output_dir: Path, verbose: bool = False):
        self.cpu2017_dir = Path(cpu2017_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.script_dir = Path(__file__).parent
        self.libs_dir = self.script_dir / 'libs'  # Add libs directory path

        # Benchmark configurations
        self.benchmarks = {
            'mcf': {
                'name': 'MCF (Minimum Cost Flow)',
                'spec_path': '505.mcf_r/src',
                'cleaner_dir': 'mcf',
                'description': 'Network flow optimization algorithm'
            },
            'lbm': {
                'name': 'LBM (Lattice Boltzmann Method)',
                'spec_path': '519.lbm_r/src',
                'cleaner_dir': 'lbm',
                'description': 'Fluid dynamics simulation'
            },
            'deepsjeng': {
                'name': 'Deepsjeng (Chess Engine)',
                'spec_path': '531.deepsjeng_r/src',
                'cleaner_dir': 'deepsjeng',
                'description': 'Chess playing engine'
            },
            'namd': {
                'name': 'NAMD (Nanoscale Molecular Dynamics)',
                'spec_path': '508.namd_r/src',
                'cleaner_dir': 'namd',
                'description': 'Scalable Molecular Dynamics software'
            }
        }

        self.results = {}

    def verify_structure(self):
        """Verify that all required cleaner directories and files exist."""
        missing = []

        if self.verbose:
            print(f"🔍 Checking cleaner structure in: {self.libs_dir}")

        # Check if libs directory exists
        if not self.libs_dir.exists():
            missing.append(f"Libs directory: {self.libs_dir}")
            print(f"\n❌ Missing libs directory: {self.libs_dir}")
            return False

        for benchmark, config in self.benchmarks.items():
            cleaner_dir = self.libs_dir / config['cleaner_dir']  # Changed from self.script_dir to self.libs_dir
            cleaner_script = cleaner_dir / 'cleaner.py'
            makefile = cleaner_dir / 'Makefile'

            if self.verbose:
                print(f"   Checking {benchmark}:")
                print(f"     Directory: {cleaner_dir}")
                print(f"     Cleaner: {cleaner_script}")
                print(f"     Makefile: {makefile}")

            if not cleaner_dir.exists():
                missing.append(f"Directory: {cleaner_dir}")
                if self.verbose:
                    print(f"     ❌ Directory missing")
            elif not cleaner_script.exists():
                missing.append(f"Cleaner script: {cleaner_script}")
                if self.verbose:
                    print(f"     ❌ cleaner.py missing")
            elif not makefile.exists():
                missing.append(f"Makefile: {makefile}")
                if self.verbose:
                    print(f"     ❌ Makefile missing")
            else:
                if self.verbose:
                    print(f"     ✅ All files found")

        if missing:
            print("\n❌ Missing required files:")
            for item in missing:
                print(f"   {item}")
            if self.verbose:
                print("\nExpected structure:")
                print(f"{self.script_dir}/")
                print("├── libs/")
                for benchmark, config in self.benchmarks.items():
                    print(f"│   ├── {config['cleaner_dir']}/")
                    print(f"│   │   ├── cleaner.py")
                    print(f"│   │   └── Makefile")
            return False

        return True

    def verify_cpu2017_structure(self):
        """Verify that CPU2017 directory has the expected benchmark directories."""
        missing = []

        if self.verbose:
            print(f"\n🔍 Checking CPU2017 structure in: {self.cpu2017_dir}")

        for benchmark, config in self.benchmarks.items():
            spec_src_path = self.cpu2017_dir / 'benchspec' / 'CPU' / config['spec_path']
            if self.verbose:
                print(f"   Checking {benchmark}: {spec_src_path}")

            if not spec_src_path.exists():
                missing.append(f"SPEC source: {spec_src_path}")
                if self.verbose:
                    print(f"     ❌ Source directory missing")
            else:
                # Count source files
                source_files = list(spec_src_path.glob('*.c')) + list(spec_src_path.glob('*.cpp')) + list(spec_src_path.glob('*.h'))
                if self.verbose:
                    print(f"     ✅ Found {len(source_files)} source files")

        if missing:
            print("\n❌ Missing SPEC CPU2017 benchmark directories:")
            for item in missing:
                print(f"   {item}")
            return False

        return True

    def run_cleaner(self, benchmark: str) -> Tuple[bool, str, List[str]]:
        """Run the cleaner for a specific benchmark."""
        config = self.benchmarks[benchmark]

        # Paths - Updated to use libs_dir
        cleaner_dir = self.libs_dir / config['cleaner_dir']  # Changed from self.script_dir to self.libs_dir
        cleaner_script = cleaner_dir / 'cleaner.py'
        spec_src_path = self.cpu2017_dir / 'benchspec' / 'CPU' / config['spec_path']
        output_path = self.output_dir / benchmark

        print(f"\n🔧 Processing {config['name']}...")
        if self.verbose:
            print(f"   Cleaner dir: {cleaner_dir}")
            print(f"   Cleaner script: {cleaner_script}")
            print(f"   Source: {spec_src_path}")
            print(f"   Output: {output_path}")
        else:
            print(f"   Source: {spec_src_path.name} → Output: {output_path.name}")

        # Verify cleaner script exists
        if not cleaner_script.exists():
            return False, f"Cleaner script not found: {cleaner_script}", []

        # Verify source directory exists
        if not spec_src_path.exists():
            return False, f"Source directory not found: {spec_src_path}", []

        try:
            # Make cleaner executable
            os.chmod(cleaner_script, 0o755)
            if self.verbose:
                print(f"   Made cleaner executable")

            # Ensure output directory exists
            output_path.mkdir(parents=True, exist_ok=True)
            if self.verbose:
                print(f"   Created output directory: {output_path}")

            # Build command with absolute paths to avoid relative path issues
            cmd = [
                sys.executable,  # Use same Python interpreter
                str(cleaner_script.resolve()),  # Absolute path to cleaner
                str(spec_src_path.resolve()),   # Absolute path to source
                str(output_path.resolve())      # Absolute path to output
            ]

            if self.verbose:
                cmd.append('-v')

            if self.verbose:
                print(f"   Running command: {' '.join(cmd)}")
                print(f"   Working directory: {cleaner_dir}")
            else:
                print(f"   Running cleaner...")

            # Run the cleaner from the cleaner's directory
            result = subprocess.run(
                cmd,
                cwd=str(cleaner_dir),  # Run from cleaner's directory
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            print(f"   Return code: {result.returncode}")

            output_lines = []
            if result.stdout:
                stdout_lines = result.stdout.strip().split('\n')
                output_lines.extend(stdout_lines)
                if self.verbose:
                    print(f"   STDOUT ({len(stdout_lines)} lines):")
                    for line in stdout_lines:
                        print(f"     {line}")
                else:
                    print(f"   STDOUT ({len(stdout_lines)} lines):")
                    for line in stdout_lines[:3]:  # Show first 3 lines in non-verbose
                        print(f"     {line}")
                    if len(stdout_lines) > 3:
                        print(f"     ... ({len(stdout_lines) - 3} more lines, use -v for full output)")

            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                output_lines.extend(stderr_lines)
                if self.verbose:
                    print(f"   STDERR ({len(stderr_lines)} lines):")
                    for line in stderr_lines:
                        print(f"     {line}")
                else:
                    print(f"   STDERR ({len(stderr_lines)} lines):")
                    for line in stderr_lines[:3]:  # Show first 3 lines in non-verbose
                        print(f"     {line}")
                    if len(stderr_lines) > 3:
                        print(f"     ... ({len(stderr_lines) - 3} more lines, use -v for full output)")

            # Check if output directory has files
            if output_path.exists():
                output_files = list(output_path.rglob('*'))
                source_files = [f for f in output_files if f.is_file() and f.suffix in ['.c', '.cpp', '.h']]
                print(f"   Output check: {len(output_files)} total files, {len(source_files)} source files")

                if len(source_files) == 0:
                    return False, "No source files in output directory", output_lines
            else:
                return False, "Output directory was not created", output_lines

            if result.returncode == 0:
                print(f"   ✅ Cleaning completed successfully")
                return True, "Success", output_lines
            else:
                print(f"   ❌ Cleaning failed with return code {result.returncode}")
                return False, f"Failed with return code {result.returncode}", output_lines

        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout after 5 minutes")
            return False, "Timeout after 5 minutes", []
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return False, f"Error: {str(e)}", []

    def copy_makefile(self, benchmark: str) -> bool:
        """Copy the Makefile to the cleaned benchmark directory."""
        config = self.benchmarks[benchmark]

        makefile_src = self.libs_dir / config['cleaner_dir'] / 'Makefile'  # Changed from self.script_dir to self.libs_dir
        output_path = self.output_dir / benchmark
        makefile_dst = output_path / 'Makefile'

        print(f"   📄 Copying Makefile from {makefile_src.name} to output directory")
        if self.verbose:
            print(f"     Source: {makefile_src}")
            print(f"     Destination: {makefile_dst}")

        try:
            if not makefile_src.exists():
                print(f"   ❌ Source Makefile not found: {makefile_src}")
                return False

            shutil.copy2(makefile_src, makefile_dst)
            print(f"   ✅ Makefile copied successfully")
            return True
        except Exception as e:
            print(f"   ❌ Failed to copy Makefile: {e}")
            return False

    def test_build(self, benchmark: str) -> Tuple[bool, str]:
        """Test building the cleaned benchmark."""
        output_path = self.output_dir / benchmark

        print(f"   🔨 Testing build for {benchmark} in {output_path}...")

        try:
            # First clean
            clean_result = subprocess.run(
                ['make', 'clean'],
                cwd=str(output_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"   Clean result: {clean_result.returncode}")

            # Then build
            build_result = subprocess.run(
                ['make'],
                cwd=str(output_path),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for build
            )

            print(f"   Build result: {build_result.returncode}")
            if self.verbose:
                if build_result.stdout:
                    print(f"   Build stdout: {build_result.stdout}")
                if build_result.stderr:
                    print(f"   Build stderr: {build_result.stderr}")
            else:
                if build_result.stdout:
                    print(f"   Build stdout: {build_result.stdout[:200]}...")
                if build_result.stderr:
                    print(f"   Build stderr: {build_result.stderr[:200]}...")

            if build_result.returncode == 0:
                print(f"   ✅ Build successful")
                return True, "Build successful"
            else:
                error_msg = build_result.stderr.strip() if build_result.stderr else "Unknown build error"
                print(f"   ⚠️  Build failed: {error_msg}")
                return False, f"Build failed: {error_msg}"

        except subprocess.TimeoutExpired:
            print(f"   ❌ Build timeout")
            return False, "Build timeout"
        except Exception as e:
            print(f"   ❌ Build error: {str(e)}")
            return False, f"Build error: {str(e)}"

    def process_benchmark(self, benchmark: str, build_test: bool = True) -> Dict:
        """Process a single benchmark completely."""
        result = {
            'benchmark': benchmark,
            'name': self.benchmarks[benchmark]['name'],
            'cleaned': False,
            'makefile_copied': False,
            'build_tested': False,
            'build_successful': False,
            'message': '',
            'output': []
        }

        print(f"\n{'='*60}")
        print(f"🚀 PROCESSING: {result['name']}")
        print(f"{'='*60}")

        # Run cleaner
        success, message, output = self.run_cleaner(benchmark)
        result['cleaned'] = success
        result['message'] = message
        result['output'] = output

        if not success:
            print(f"❌ Cleaning failed: {message}")
            return result

        # Copy Makefile
        result['makefile_copied'] = self.copy_makefile(benchmark)

        # Test build if requested
        if build_test and result['makefile_copied']:
            result['build_tested'] = True
            build_success, build_message = self.test_build(benchmark)
            result['build_successful'] = build_success
            if not build_success:
                result['message'] += f" | {build_message}"

        return result

    def process_all(self, benchmarks: Optional[List[str]] = None, build_test: bool = True) -> Dict:
        """Process all specified benchmarks."""
        if benchmarks is None:
            benchmarks = list(self.benchmarks.keys())

        print("🚀 Starting Simple SPEC processing...")
        if self.verbose:
            print(f"Script directory: {self.script_dir}")
            print(f"Libs directory: {self.libs_dir}")  # Add libs directory info
            print(f"CPU2017 directory: {self.cpu2017_dir}")
            print(f"Output directory: {self.output_dir}")
            print(f"Benchmarks to process: {', '.join(benchmarks)}")
        else:
            print(f"Processing {len(benchmarks)} benchmarks: {', '.join(benchmarks)}")

        # Verify structure
        if not self.verify_structure():
            return {'error': 'Missing required cleaner files'}

        if not self.verify_cpu2017_structure():
            return {'error': 'Missing SPEC CPU2017 benchmark directories'}

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.verbose:
            print(f"\n✅ Created output directory: {self.output_dir}")
        else:
            print(f"✅ Output directory ready: {self.output_dir}")

        # Process each benchmark
        results = {}
        for benchmark in benchmarks:
            if benchmark not in self.benchmarks:
                print(f"❌ Unknown benchmark: {benchmark}")
                continue

            results[benchmark] = self.process_benchmark(benchmark, build_test)

        return results

    def print_summary(self, results: Dict):
        """Print a summary of the processing results."""
        if 'error' in results:
            print(f"\n❌ Simple SPEC processing failed: {results['error']}")
            return

        print("\n" + "="*60)
        print("📊 SIMPLE SPEC SUMMARY")
        print("="*60)

        total = len(results)
        cleaned = sum(1 for r in results.values() if r['cleaned'])
        built = sum(1 for r in results.values() if r['build_successful'])

        print(f"Total benchmarks: {total}")
        print(f"Successfully cleaned: {cleaned}/{total}")
        print(f"Successfully built: {built}/{total}")

        print("\nDetailed results:")
        for benchmark, result in results.items():
            status_icons = []
            if result['cleaned']:
                status_icons.append('🧹')
            if result['makefile_copied']:
                status_icons.append('📄')
            if result['build_successful']:
                status_icons.append('🔨')
            elif result['build_tested']:
                status_icons.append('⚠️')

            status = ''.join(status_icons) if status_icons else '❌'
            print(f"  {status} {result['name']}")
            if result['message'] and not result['cleaned']:
                print(f"      Error: {result['message']}")

        print("\nLegend: 🧹=Cleaned 📄=Makefile 🔨=Built ⚠️=Build Failed ❌=Failed")

        # Show where outputs are
        if cleaned > 0:
            print(f"\n📁 Cleaned benchmarks available in: {self.output_dir}")
            for benchmark, result in results.items():
                if result['cleaned']:
                    output_path = self.output_dir / benchmark
                    print(f"   {benchmark}: {output_path}")

                    # List some files to verify
                    if output_path.exists():
                        files = list(output_path.glob('*'))
                        source_files = [f for f in files if f.suffix in ['.c', '.cpp', '.h']]
                        print(f"      Files: {len(files)} total, {len(source_files)} source files")

def main():
    parser = argparse.ArgumentParser(
        description='Simple SPEC - Process CPU2017 benchmarks to remove proprietary code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all benchmarks with default paths
  python3 simple_spec.py
  # Input:  ./cpu2017/benchspec/CPU/505.mcf_r/src -> Output: ./benchmarks_cleaned/mcf
  # Input:  ./cpu2017/benchspec/CPU/519.lbm_r/src -> Output: ./benchmarks_cleaned/lbm
  # Input:  ./cpu2017/benchspec/CPU/531.deepsjeng_r/src -> Output: ./benchmarks_cleaned/deepsjeng

  # Specify CPU2017 directory
  python3 simple_spec.py --cpu2017-dir "./cpu2017"

  # Custom output directory
  python3 simple_spec.py --output-dir "./my_cleaned_benchmarks"

  # Process specific benchmarks only
  python3 simple_spec.py --benchmarks mcf namd

Expected directory structure:
  main_dir/
  ├── cpu2017/
  │   └── benchspec/
  │       └── CPU/
  │           ├── 505.mcf_r/src/
  │           ├── 508.namd_r/src/
  │           ├── 519.lbm_r/src/
  │           └── 531.deepsjeng_r/src/
  ├── libs/
  │   ├── lbm/
  │   │   ├── cleaner.py
  │   │   └── Makefile
  │   ├── mcf/
  │   │   ├── cleaner.py
  │   │   └── Makefile│
  │   ├── namd/
  │   │   ├── apoa1.input
  │   │   ├── cleaner.py
  │   │   └── Makefile
  │   └── deepsjeng/
  │       ├── cleaner.py
  │       └── Makefile
  ├── simple_spec.py
  └── benchmarks_cleaned/  (created by script)
      ├── mcf/
      ├── lbm/
      ├── namd/
      └── deepsjeng/
        """
    )

    parser.add_argument(
        '--cpu2017-dir',
        default='./cpu2017',
        help='Path to CPU2017 directory (default: ./cpu2017)'
    )

    parser.add_argument(
        '--output-dir',
        default='./benchmarks_cleaned',
        help='Output directory for cleaned benchmarks (default: ./benchmarks_cleaned)'
    )

    parser.add_argument(
        '--benchmarks',
        nargs='*',
        choices=['mcf', 'lbm', 'deepsjeng','namd'],
        help='Specific benchmarks to process (default: all)'
    )

    parser.add_argument(
        '--no-build-test',
        action='store_true',
        help='Skip build testing after cleaning'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Create the Simple SPEC processor
    processor = SimpleSpec(
        cpu2017_dir=args.cpu2017_dir,
        output_dir=args.output_dir,
        verbose=args.verbose
    )

    # Process benchmarks
    results = processor.process_all(
        benchmarks=args.benchmarks,
        build_test=not args.no_build_test
    )

    # Print summary
    processor.print_summary(results)

    # Exit with appropriate code
    if 'error' in results:
        sys.exit(1)
    elif not all(r['cleaned'] for r in results.values()):
        sys.exit(2)  # Some benchmarks failed
    else:
        sys.exit(0)  # All successful

if __name__ == '__main__':
    main()