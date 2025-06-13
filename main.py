#!/usr/bin/env python3
"""
Main CPU2017 Installation and Simple SPEC Runner

This script orchestrates the complete process:
1. Install CPU2017 from ISO
2. Run Simple SPEC to process benchmarks
3. Clean up and provide summary

Usage:
    python3 main.py [options]
    python3 main.py --iso-path "cpu2017-1_0_5.iso"
    python3 main.py --install-dir "my_cpu2017" --output-dir "my_benchmarks"
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import Optional

# Import our modules
from installation import main as install_cpu2017
from simple_spec import SimpleSpec

class CPU2017Runner:
    def __init__(self, iso_path: str, install_dir: str, output_dir: str, verbose: bool = False):
        self.iso_path = Path(iso_path)
        self.install_dir = Path(install_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.script_dir = Path(__file__).parent

    def validate_inputs(self):
        """Validate input parameters and files."""
        print("🔍 Validating inputs...")
        
        # Check if ISO exists
        if not self.iso_path.exists():
            print(f"❌ ISO file not found: {self.iso_path}")
            return False
        
        print(f"✅ ISO file found: {self.iso_path}")
        
        # Check if cleaner directories exist
        required_cleaners = ['mcf', 'lbm', 'deepsjeng']
        for cleaner in required_cleaners:
            cleaner_dir = self.script_dir / cleaner
            cleaner_script = cleaner_dir / 'cleaner.py'
            makefile = cleaner_dir / 'Makefile'
            
            if not cleaner_dir.exists():
                print(f"❌ Cleaner directory missing: {cleaner_dir}")
                return False
            if not cleaner_script.exists():
                print(f"❌ Cleaner script missing: {cleaner_script}")
                return False
            if not makefile.exists():
                print(f"❌ Makefile missing: {makefile}")
                return False
        
        print("✅ All cleaner directories and files found")
        return True

    def install_cpu2017(self):
        """Install CPU2017 from ISO."""
        print("\n" + "="*60)
        print("📦 INSTALLING CPU2017")
        print("="*60)
        
        if self.install_dir.exists():
            print(f"⚠️  Install directory already exists: {self.install_dir}")
            response = input("Do you want to remove it and reinstall? (y/N): ")
            if response.lower() in ['y', 'yes']:
                print(f"🗑️  Removing existing directory: {self.install_dir}")
                shutil.rmtree(self.install_dir)
            else:
                print("ℹ️  Using existing installation")
                return True
        
        try:
            print(f"📦 Installing CPU2017 from {self.iso_path}")
            print(f"📁 Installation directory: {self.install_dir}")
            
            # Call the installation module
            install_cpu2017(str(self.iso_path), str(self.install_dir))
            
            # Verify installation
            if self.verify_installation():
                print("✅ CPU2017 installation completed successfully")
                return True
            else:
                print("❌ CPU2017 installation verification failed")
                return False
                
        except Exception as e:
            print(f"❌ CPU2017 installation failed: {e}")
            return False

    def verify_installation(self):
        """Verify that CPU2017 was installed correctly."""
        print("🔍 Verifying CPU2017 installation...")
        
        # Check for benchspec directory
        benchspec_dir = self.install_dir / 'benchspec' / 'CPU'
        if not benchspec_dir.exists():
            print(f"❌ Benchspec directory not found: {benchspec_dir}")
            return False
        
        # Check for required benchmark directories
        required_benchmarks = {
            '505.mcf_r': 'MCF',
            '519.lbm_r': 'LBM', 
            '531.deepsjeng_r': 'Deepsjeng'
        }
        
        missing_benchmarks = []
        for benchmark_id, name in required_benchmarks.items():
            benchmark_dir = benchspec_dir / benchmark_id / 'src'
            if not benchmark_dir.exists():
                missing_benchmarks.append(f"{name} ({benchmark_id})")
            else:
                # Count source files
                source_files = list(benchmark_dir.glob('*.c')) + list(benchmark_dir.glob('*.cpp'))
                print(f"   ✅ {name}: {len(source_files)} source files found")
        
        if missing_benchmarks:
            print(f"❌ Missing benchmark directories: {', '.join(missing_benchmarks)}")
            return False
        
        print("✅ All required benchmarks found")
        return True

    def run_simple_spec(self, benchmarks: Optional[list] = None, build_test: bool = True):
        """Run Simple SPEC to process benchmarks."""
        print("\n" + "="*60)
        print("🚀 RUNNING SIMPLE SPEC")
        print("="*60)
        
        try:
            # Create Simple SPEC processor
            processor = SimpleSpec(
                cpu2017_dir=self.install_dir,
                output_dir=self.output_dir,
                verbose=self.verbose
            )
            
            # Process benchmarks
            results = processor.process_all(
                benchmarks=benchmarks,
                build_test=build_test
            )
            
            # Print summary
            processor.print_summary(results)
            
            return results
            
        except Exception as e:
            print(f"❌ Simple SPEC processing failed: {e}")
            return {'error': str(e)}

    def cleanup_installation(self, keep_install: bool = False):
        """Clean up installation files if requested."""
        if not keep_install:
            print(f"\n🗑️  Cleaning up installation directory: {self.install_dir}")
            try:
                shutil.rmtree(self.install_dir)
                print("✅ Installation directory removed")
            except Exception as e:
                print(f"⚠️  Failed to remove installation directory: {e}")

    def run_complete_process(self, benchmarks: Optional[list] = None, 
                           build_test: bool = True, cleanup: bool = False):
        """Run the complete process from installation to benchmark processing."""
        print("🚀 Starting CPU2017 Installation and Simple SPEC Processing")
        print(f"📁 Script directory: {self.script_dir}")
        print(f"💿 ISO path: {self.iso_path}")
        print(f"📦 Install directory: {self.install_dir}")
        print(f"📂 Output directory: {self.output_dir}")
        
        if benchmarks:
            print(f"🎯 Target benchmarks: {', '.join(benchmarks)}")
        else:
            print("🎯 Target benchmarks: all (mcf, lbm, deepsjeng)")
        
        # Step 1: Validate inputs
        if not self.validate_inputs():
            print("❌ Input validation failed")
            return False
        
        # Step 2: Install CPU2017
        if not self.install_cpu2017():
            print("❌ CPU2017 installation failed")
            return False
        
        # Step 3: Run Simple SPEC
        results = self.run_simple_spec(benchmarks=benchmarks, build_test=build_test)
        
        # Step 4: Check results
        if 'error' in results:
            print(f"❌ Simple SPEC failed: {results['error']}")
            if cleanup:
                self.cleanup_installation()
            return False
        
        # Step 5: Final summary
        print("\n" + "="*60)
        print("🎉 PROCESS COMPLETED")
        print("="*60)
        
        successful_benchmarks = [name for name, result in results.items() if result['cleaned']]
        built_benchmarks = [name for name, result in results.items() if result['build_successful']]
        
        print(f"✅ Successfully processed: {len(successful_benchmarks)}/{len(results)} benchmarks")
        print(f"🔨 Successfully built: {len(built_benchmarks)}/{len(results)} benchmarks")
        
        if successful_benchmarks:
            print(f"\n📁 Cleaned benchmarks available in: {self.output_dir}")
            for benchmark in successful_benchmarks:
                benchmark_dir = self.output_dir / benchmark
                print(f"   📂 {benchmark}: {benchmark_dir}")
        
        # Step 6: Optional cleanup
        if cleanup:
            self.cleanup_installation()
        else:
            print(f"\nℹ️  CPU2017 installation preserved at: {self.install_dir}")
            print("   Use --cleanup to remove it automatically")
        
        return len(successful_benchmarks) == len(results)

def main():
    parser = argparse.ArgumentParser(
        description='CPU2017 Installation and Simple SPEC Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Complete workflow:
1. Install CPU2017 from ISO
2. Process benchmarks to remove proprietary code
3. Test builds (optional)
4. Clean up (optional)

Examples:
  # Basic usage with default paths
  python3 main.py
  
  # Specify custom paths
  python3 main.py --iso-path "cpu2017-1_0_5.iso" --install-dir "cpu2017" --output-dir "cleaned_benchmarks"
  
  # Process specific benchmarks only
  python3 main.py --benchmarks mcf lbm
  
  # Skip build testing and clean up after
  python3 main.py --no-build-test --cleanup
  
  # Verbose output
  python3 main.py -v

Required files in current directory:
  ├── main.py (this script)
  ├── installation.py
  ├── simple_spec.py
  ├── cpu2017-1_0_5.iso (or specified ISO)
  ├── mcf/
  │   ├── cleaner.py
  │   └── Makefile
  ├── lbm/
  │   ├── cleaner.py
  │   └── Makefile
  └── deepsjeng/
      ├── cleaner.py
      └── Makefile
        """
    )
    
    parser.add_argument(
        '--iso-path',
        default='cpu2017-1_0_5.iso',
        help='Path to CPU2017 ISO file (default: cpu2017-1_0_5.iso)'
    )
    
    parser.add_argument(
        '--install-dir',
        default='cpu2017',
        help='CPU2017 installation directory (default: cpu2017)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='benchmarks_cleaned',
        help='Output directory for cleaned benchmarks (default: benchmarks_cleaned)'
    )
    
    parser.add_argument(
        '--benchmarks',
        nargs='*',
        choices=['mcf', 'lbm', 'deepsjeng'],
        help='Specific benchmarks to process (default: all)'
    )
    
    parser.add_argument(
        '--no-build-test',
        action='store_true',
        help='Skip build testing after cleaning'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove CPU2017 installation after processing'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Create the runner
    runner = CPU2017Runner(
        iso_path=args.iso_path,
        install_dir=args.install_dir,
        output_dir=args.output_dir,
        verbose=args.verbose
    )
    
    # Run the complete process
    success = runner.run_complete_process(
        benchmarks=args.benchmarks,
        build_test=not args.no_build_test,
        cleanup=args.cleanup
    )
    
    # Exit with appropriate code
    if success:
        print("\n🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some operations failed. Check the output above for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()