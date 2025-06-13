# SPEC CPU2017 Benchmark Unspeccer

A comprehensive tool for converting SPEC CPU2017 benchmarks back to their open-source versions, removing proprietary modifications and restoring original functionality.

## Overview

This project automatically processes three key SPEC CPU2017 benchmarks:

- **505.mcf_r** - MCF (Minimum Cost Flow) network optimization
- **519.lbm_r** - LBM (Lattice Boltzmann Method) fluid dynamics simulation
- **531.deepsjeng_r** - Deepsjeng chess engine

## Features

✅ **Removes SPEC-specific code** - Strips proprietary modifications
✅ **Restores original functionality** - Brings back timing, randomization, UCI interface
✅ **Multi-compiler support** - GCC, Clang, and NVCC
✅ **Cross-platform** - Linux, macOS, Windows
✅ **Automated batch processing** - Process all benchmarks with one command
✅ **Comprehensive build system** - Debug, release, profiling, sanitizers

## Project Structure

```
spec-unspeccer/
├── cpu2017/                          # Your SPEC CPU2017 installation
│   └── benchspec/CPU/
│       ├── 505.mcf_r/src/           # MCF source files
│       ├── 519.lbm_r/src/           # LBM source files
│       └── 531.deepsjeng_r/src/     # Deepsjeng source files
├── mcf/
│   ├── cleaner.py                   # MCF-specific cleaner
│   └── Makefile                     # MCF multi-compiler Makefile
├── lbm/
│   ├── cleaner.py                   # LBM-specific cleaner
│   └── Makefile                     # LBM multi-compiler Makefile
├── deepsjeng/
│   ├── cleaner.py                   # Deepsjeng-specific cleaner
│   └── Makefile                     # Deepsjeng multi-compiler Makefile
├── spec_batch_cleaner.py            # Main batch processing script
├── benchmarks_cleaned/              # Output directory (created automatically)
│   ├── mcf/                        # Cleaned MCF benchmark
│   ├── lbm/                        # Cleaned LBM benchmark
│   └── deepsjeng/                  # Cleaned Deepsjeng benchmark
└── README.md                       # This file
```

## Prerequisites

### Required

- **Python 3.6+** - For running the cleaning scripts
- **Make** - For building the benchmarks
- **A C/C++ compiler** - GCC, Clang, or NVCC

### Optional but Recommended

- **GCC** - Best performance for numerical benchmarks
- **Clang** - Better for development and debugging
- **NVCC** - For CUDA acceleration (experimental)
- **OpenMP** - For parallel processing

## Setup

### 1. Install Compilers

#### Linux (Ubuntu/Debian)

```bash
# GCC (recommended for performance)
sudo apt update
sudo apt install gcc g++ make

# Clang (good for development)
sudo apt install clang

# OpenMP support
sudo apt install libomp-dev

# CUDA (optional)
# Follow NVIDIA CUDA installation guide
```

#### macOS

```bash
# Install Xcode Command Line Tools (includes Clang)
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install real GCC for better performance (optional)
brew install gcc

# Install OpenMP for Clang
brew install libomp

# CUDA (optional)
# Download from NVIDIA website
```

#### Windows

```bash
# Using MSYS2/MinGW-w64
# Download from https://www.msys2.org/

# Or Visual Studio Build Tools
# Download from Microsoft
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
```

## Quick Start

### 1. Place SPEC CPU2017 Source

Ensure your SPEC CPU2017 source is in the expected location:

```
./cpu2017/benchspec/CPU/505.mcf_r/src/
./cpu2017/benchspec/CPU/519.lbm_r/src/
./cpu2017/benchspec/CPU/531.deepsjeng_r/src/
```

### 2. Run Batch Cleaner

```bash
# Process all benchmarks with default settings
python3 spec_batch_cleaner.py

# With verbose output
python3 spec_batch_cleaner.py -v

# Custom paths
python3 spec_batch_cleaner.py --cpu2017-dir "./my_cpu2017" --output-dir "./my_output"

# Process specific benchmarks only
python3 spec_batch_cleaner.py --benchmarks mcf lbm
```

### 3. Build and Test

```bash
# Navigate to a cleaned benchmark
cd benchmarks_cleaned/mcf

# Build with default compiler
make

# Test the build
make test
```

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

### Common Issues

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

1. Create a new directory: `mkdir new_benchmark/`
2. Add `cleaner.py` script following existing patterns
3. Add `Makefile` with multi-compiler support
4. Update `spec_batch_cleaner.py` to include new benchmark

### Improving Cleaners

1. Test with individual cleaner: `python3 cleaner.py input/ output/`
2. Verify functionality of cleaned code
3. Update patterns in cleaner script
4. Test with batch cleaner

### Reporting Issues

Please include:

- Operating system and version
- Compiler versions (`gcc --version`, `clang --version`)
- Full error output with `-v` flag
- Steps to reproduce

## License

This project restores SPEC CPU2017 benchmarks to their original open-source versions. Each benchmark retains its original license:

- **MCF**: Academic/research use
- **LBM**: Open source
- **Deepsjeng**: GPL (derived from Sjeng)

The cleaning scripts and build system are provided under MIT license.

## Acknowledgments

- Original benchmark authors
- SPEC CPU2017 consortium
- Open source communities maintaining the original codebases

---

**Note**: This tool removes SPEC-specific modifications to restore original functionality. It is intended for research, education, and development purposes. For official SPEC benchmarking, use the original SPEC CPU2017 suite.
