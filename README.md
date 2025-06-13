# SPEC CPU2017 Benchmark Unspeccer

A comprehensive tool for converting SPEC CPU2017 benchmarks back to their open-source versions, removing proprietary modifications and restoring original functionality.

## Overview

This project automatically processes three key SPEC CPU2017 benchmarks:

- **505.mcf_r** - MCF (Minimum Cost Flow) network optimization
- **519.lbm_r** - LBM (Lattice Boltzmann Method) fluid dynamics simulation
- **531.deepsjeng_r** - Deepsjeng chess engine

## Features

✅ **Automated ISO Installation** - Installs CPU2017 from ISO across platforms  
✅ **Removes SPEC-specific code** - Strips proprietary modifications  
✅ **Restores original functionality** - Brings back timing, randomization, UCI interface  
✅ **Multi-compiler support** - GCC, Clang, and NVCC  
✅ **Cross-platform** - Linux, macOS, Windows  
✅ **Automated batch processing** - Process all benchmarks with one command  
✅ **Comprehensive build system** - Debug, release, profiling, sanitizers  

## Project Structure

```
spec-unspeccer/
├── main.py                          # Main orchestrator script
├── installation.py                  # ISO installation module
├── simple_spec.py                   # Benchmark processing module
├── cpu2017-1_0_5.iso               # Your SPEC CPU2017 ISO file
├── libs/                           # Cleaner libraries directory
│   ├── mcf/
│   │   ├── cleaner.py              # MCF-specific cleaner
│   │   └── Makefile                # MCF multi-compiler Makefile
│   ├── lbm/
│   │   ├── cleaner.py              # LBM-specific cleaner
│   │   └── Makefile                # LBM multi-compiler Makefile
│   └── deepsjeng/
│       ├── cleaner.py              # Deepsjeng-specific cleaner
│       └── Makefile                # Deepsjeng multi-compiler Makefile
├── cpu2017/                        # CPU2017 installation (created automatically)
│   └── benchspec/CPU/
│       ├── 505.mcf_r/src/         # MCF source files
│       ├── 519.lbm_r/src/         # LBM source files
│       └── 531.deepsjeng_r/src/   # Deepsjeng source files
├── benchmarks_cleaned/             # Output directory (created automatically)
│   ├── mcf/                       # Cleaned MCF benchmark
│   ├── lbm/                       # Cleaned LBM benchmark
│   └── deepsjeng/                 # Cleaned Deepsjeng benchmark
└── README.md                      # This file
```

## Prerequisites

### Required

- **Python 3.6+** - For running the cleaning scripts
- **Make** - For building the benchmarks
- **A C/C++ compiler** - GCC, Clang, or NVCC
- **7-Zip** (Windows) or **mount utilities** (Linux/macOS) - For ISO extraction/mounting

### Optional but Recommended

- **GCC** - Best performance for numerical benchmarks
- **Clang** - Better for development and debugging
- **NVCC** - For CUDA acceleration (experimental)
- **OpenMP** - For parallel processing

## Setup

### 1. Install System Dependencies

#### Linux (Ubuntu/Debian)

```bash
# Essential tools
sudo apt update
sudo apt install python3 make

# GCC (recommended for performance)
sudo apt install gcc g++

# Clang (good for development)
sudo apt install clang

# OpenMP support
sudo apt install libomp-dev

# For ISO mounting (usually pre-installed)
sudo apt install mount

# CUDA (optional)
# Follow NVIDIA CUDA installation guide
```

#### macOS

```bash
# Install Xcode Command Line Tools (includes Clang and make)
xcode-select --install

# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install real GCC for better performance (optional)
brew install gcc

# Install OpenMP for Clang
brew install libomp

# Python3 should be pre-installed, but you can update it
brew install python3

# CUDA (optional)
# Download from NVIDIA website
```

#### Windows

```bash
# Install 7-Zip (required for ISO extraction)
# Download from https://www.7-zip.org/

# Using MSYS2/MinGW-w64 for Unix-like environment
# Download from https://www.msys2.org/

# Or Visual Studio Build Tools
# Download from Microsoft

# Python 3
# Download from https://www.python.org/
```

### 2. Verify Installation

```bash
# Check Python
python3 --version

# Check compilers
gcc --version
clang --version    # Optional
nvcc --version     # Optional

# Check make
make --version

# Check 7-Zip (Windows only)
7z --help         # Windows
```

## Quick Start

### 1. Place Files

Ensure you have the required files in your project directory:

```
your_project/
├── main.py
├── installation.py
├── simple_spec.py
├── cpu2017-1_0_5.iso              # Your SPEC CPU2017 ISO
└── libs/
    ├── mcf/
    │   ├── cleaner.py
    │   └── Makefile
    ├── lbm/
    │   ├── cleaner.py
    │   └── Makefile
    └── deepsjeng/
        ├── cleaner.py
        └── Makefile
```

### 2. Run Complete Process

```bash
# Basic usage - installs CPU2017 and processes all benchmarks
python3 main.py

# With verbose output
python3 main.py -v

# Custom paths
python3 main.py --iso-path "cpu2017-1_0_5.iso" --install-dir "cpu2017" --output-dir "cleaned_benchmarks"

# Process specific benchmarks only
python3 main.py --benchmarks mcf lbm

# Skip build testing to save time
python3 main.py --no-build-test

# Clean up CPU2017 installation after processing
python3 main.py --cleanup
```

### 3. Manual Processing (Alternative)

If you already have CPU2017 installed, you can use the processing script directly:

```bash
# Process all benchmarks with existing CPU2017 installation
python3 simple_spec.py --cpu2017-dir "./cpu2017"

# Process specific benchmarks
python3 simple_spec.py --benchmarks mcf lbm

# Custom output directory
python3 simple_spec.py --output-dir "./my_cleaned_benchmarks"
```

### 4. Build and Test

```bash
# Navigate to a cleaned benchmark
cd benchmarks_cleaned/mcf

# Build with default compiler
make

# Test the build
make test
```

## Main Script Usage

The `main.py` script orchestrates the complete workflow:

### Command Line Options

```bash
python3 main.py [options]

Options:
  --iso-path PATH       Path to CPU2017 ISO file (default: cpu2017-1_0_5.iso)
  --install-dir DIR     CPU2017 installation directory (default: cpu2017)
  --output-dir DIR      Output directory for cleaned benchmarks (default: benchmarks_cleaned)
  --benchmarks LIST     Specific benchmarks to process: mcf, lbm, deepsjeng (default: all)
  --no-build-test       Skip build testing after cleaning
  --cleanup             Remove CPU2017 installation after processing
  -v, --verbose         Verbose output
  -h, --help           Show help message
```

### Workflow Steps

1. **Validation** - Checks for ISO file and cleaner libraries
2. **Installation** - Extracts/mounts ISO and runs CPU2017 installer
3. **Processing** - Runs cleaners to remove proprietary code
4. **Building** - Tests that cleaned code compiles successfully
5. **Cleanup** - Optionally removes temporary installation files

## Build Options

Each benchmark supports multiple build configurations:

### Compiler Selection

```bash
# Use default compiler (gcc on Linux, clang on macOS)
make

# Force specific compiler
make CC=gcc CXX=g++
make CC=clang CXX=clang++
make CC=nvcc          # CUDA builds

# Convenience targets
make gcc              # Build with GCC
make clang            # Build with Clang
make nvcc             # Build with NVCC
```

### Build Variants

```bash
# Debug build (symbols, assertions)
make debug

# Optimized release build
make release

# Fast math optimizations
make fast

# Parallel processing (if OpenMP available)
make openmp

# Profiling build
make profile
```

### Analysis and Debugging

```bash
# Memory debugging (GCC/Clang only)
make asan             # AddressSanitizer

# Thread debugging (GCC/Clang only)
make tsan             # ThreadSanitizer

# Static analysis
make analyze          # Uses cppcheck

# Profile-guided optimization
make pgo-generate     # Step 1: Generate profiles
# ... run benchmark ...
make pgo-use          # Step 2: Use profiles for optimization
```

### CUDA-Specific (NVCC only)

```bash
# CUDA debug build
make cuda-debug

# CUDA optimized build
make cuda-release
```

### Information and Help

```bash
# Show compiler detection results
make compiler-info

# Show detected source files
make list-sources

# Show all available targets
make help
```

## Benchmark-Specific Usage

### MCF (Minimum Cost Flow)

```bash
cd benchmarks_cleaned/mcf

# Build and create test input
make create-test

# Run basic test
make test

# Run benchmark
make benchmark

# OpenMP parallel version
make openmp
./mcf test.inp
```

### LBM (Lattice Boltzmann Method)

```bash
cd benchmarks_cleaned/lbm

# Build and test
make test

# Performance test
make perf-test

# Large workload test
make large-test

# Test with obstacle geometry
make test-obstacle

# Vectorized build for better performance
make vectorize
```

### Deepsjeng (Chess Engine)

```bash
cd benchmarks_cleaned/deepsjeng

# Build and test
make test

# The chess engine is now restored to original functionality
./sjeng --help

# For actual chess play, you'd integrate with a UCI-compatible interface
```

## Platform-Specific Notes

### Linux

- Uses `mount` command to mount ISO files
- Requires `sudo` for mounting operations
- Supports both GCC and Clang compilers out of the box

### macOS

- Uses `hdiutil` for ISO mounting (built-in)
- Clang is the default compiler (from Xcode Command Line Tools)
- GCC can be installed via Homebrew for better numerical performance

### Windows

- Uses 7-Zip for ISO extraction (must be installed separately)
- Runs `.bat` installer instead of shell script
- MSYS2/MinGW-w64 recommended for Unix-like build environment
- Visual Studio Build Tools also supported

## Performance Tips

### For Maximum Performance

```bash
# Use GCC with all optimizations
make CC=gcc release

# Add OpenMP if your problem supports parallelization
make CC=gcc openmp release

# Use profile-guided optimization for production
make CC=gcc pgo-generate
# ... run representative workload ...
make CC=gcc pgo-use release
```

### For Development

```bash
# Use Clang with debugging
make CC=clang debug

# Add sanitizers for bug detection
make CC=clang asan

# Static analysis
make CC=clang analyze
```

### For CUDA Acceleration (Experimental)

```bash
# CUDA release build
make CC=nvcc cuda-release

# Note: CUDA support is experimental and may require code modifications
```

## Troubleshooting

### Installation Issues

#### ISO Not Found

```bash
# Ensure ISO file exists and path is correct
ls -la cpu2017-1_0_5.iso

# Try absolute path
python3 main.py --iso-path "/full/path/to/cpu2017-1_0_5.iso"
```

#### Permission Denied (Linux/macOS)

```bash
# Ensure you can use sudo for mounting
sudo echo "Sudo access verified"

# On some systems, you might need to add user to disk group
sudo usermod -a -G disk $USER
# Log out and back in
```

#### 7-Zip Not Found (Windows)

```bash
# Install 7-Zip from https://www.7-zip.org/
# Or add to PATH if already installed
set PATH=%PATH%;C:\Program Files\7-Zip
```

### Build Issues

#### OpenMP Not Found (macOS)

```bash
# Install OpenMP for Clang
brew install libomp

# Or use GCC
brew install gcc
make CC=gcc-13 openmp
```

#### Compiler Not Found

```bash
# Check available compilers
which gcc clang nvcc

# On macOS, 'gcc' might actually be Clang
gcc --version
```

#### Build Failures

```bash
# Try with verbose output
make -v

# Check compiler detection
make compiler-info

# Use debug build for better error messages
make debug
```

#### Missing Dependencies

```bash
# Install development tools
# Ubuntu/Debian:
sudo apt install build-essential

# macOS:
xcode-select --install

# Check for missing libraries
ldd ./executable_name  # Linux
otool -L ./executable_name  # macOS
```

### Performance Issues

#### Slow Builds

```bash
# Use parallel make
make -j$(nproc)        # Linux
make -j$(sysctl -n hw.ncpu)  # macOS

# Use ccache if available
export CC="ccache gcc"
make
```

#### Runtime Performance

```bash
# Ensure you're using optimized build
make release

# Check if OpenMP is being used
export OMP_NUM_THREADS=4
./your_benchmark

# Profile the application
make profile
./your_benchmark
gprof ./your_benchmark gmon.out > analysis.txt
```

## Advanced Usage

### Custom Compiler Flags

```bash
# Add custom optimization flags
make CFLAGS="-O3 -march=native -flto" CXXFLAGS="-O3 -march=native -flto"

# Add preprocessor definitions
make CFLAGS="-DCUSTOM_SETTING=1"
```

### Cross-Compilation

```bash
# For ARM targets
make CC=aarch64-linux-gnu-gcc CXX=aarch64-linux-gnu-g++

# For specific architectures
make CFLAGS="-march=skylake-avx512"
```

### Integration with Other Tools

```bash
# Use with Intel compiler
make CC=icc CXX=icpc

# Use with PGI/NVIDIA HPC compiler
make CC=pgcc CXX=pgc++
```

## Contributing

### Adding New Benchmarks

1. Create a new directory: `mkdir libs/new_benchmark/`
2. Add `cleaner.py` script following existing patterns
3. Add `Makefile` with multi-compiler support
4. Update `simple_spec.py` to include new benchmark
5. Update `main.py` validation if needed

### Improving Cleaners

1. Test with individual cleaner: `python3 libs/benchmark/cleaner.py input/ output/`
2. Verify functionality of cleaned code
3. Update patterns in cleaner script
4. Test with batch cleaner: `python3 simple_spec.py --benchmarks benchmark`

### Reporting Issues

Please include:

- Operating system and version
- Python version (`python3 --version`)
- Compiler versions (`gcc --version`, `clang --version`)
- Full error output with `-v` flag
- Steps to reproduce
- ISO file name and version if installation-related

## License

This project restores SPEC CPU2017 benchmarks to their original open-source versions. Each benchmark retains its original license:

- **MCF**: Academic/research use
- **LBM**: Open source
- **Deepsjeng**: GPL (derived from Sjeng)

The cleaning scripts and build system are provided under MIT license.


**Note**: This tool removes SPEC-specific modifications to restore original functionality. It is intended for research, education, and development purposes. For official SPEC benchmarking, use the original SPEC CPU2017 suite.