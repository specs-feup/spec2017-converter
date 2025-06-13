# Makefile for cleaned LBM (Lattice Boltzmann Method) fluid dynamics simulation
# Original LBM simulation restored from SPEC CPU2017 version
# Supports GCC, Clang, and NVCC

# Compiler selection (can be overridden: make CC=clang CXX=clang++)
CC ?= gcc
CXX ?= g++

# Detect compiler type for both C and C++
CC_NAME := $(notdir $(CC))
CXX_NAME := $(notdir $(CXX))

# Determine if we're using NVCC
ifeq ($(CC_NAME),nvcc)
    USING_NVCC = 1
    COMPILER_INFO = "NVIDIA NVCC"
else ifeq ($(CXX_NAME),nvcc)
    USING_NVCC = 1
    COMPILER_INFO = "NVIDIA NVCC"
else
    CC_TYPE := $(shell $(CC) --version 2>&1 | head -n1)
    CXX_TYPE := $(shell $(CXX) --version 2>&1 | head -n1)
    ifneq (,$(findstring clang,$(CC_TYPE)))
        COMPILER_INFO = "Clang"
    else ifneq (,$(findstring gcc,$(CC_TYPE)))
        COMPILER_INFO = "GCC"
    else
        COMPILER_INFO = "Unknown"
    endif
endif

# Base optimization flags
BASE_CFLAGS = -O3
LDFLAGS =
LIBS = -lm

# Compiler-specific settings
ifdef USING_NVCC
    # NVIDIA NVCC
    CFLAGS = $(BASE_CFLAGS) -Xcompiler -fomit-frame-pointer
    CXXFLAGS = $(CFLAGS)
    OPENMP_FLAGS = -Xcompiler -fopenmp
    OPENMP_LIBS = -lgomp
    ARCH_FLAGS = -arch=sm_35
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -Xcompiler -funroll-loops
    NATIVE_FLAGS =
    WALL_FLAGS = -Xcompiler -Wall,-Wextra
    DEBUG_FLAGS = -g -G -Xcompiler -DDEBUG
    SANITIZER_FLAGS =
    PROFILE_FLAGS = -Xcompiler -pg
    VECTORIZE_FLAGS =
else ifneq (,$(findstring clang,$(CC_TYPE)))
    # Clang
    CFLAGS = $(BASE_CFLAGS) -funroll-loops -fomit-frame-pointer
    CXXFLAGS = $(CFLAGS)
    NATIVE_FLAGS = -march=native -mtune=native
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -funroll-loops
    WALL_FLAGS = -Wall -Wextra
    DEBUG_FLAGS = -g -DDEBUG
    SANITIZER_FLAGS = -fsanitize=address -fno-omit-frame-pointer
    PROFILE_FLAGS = -pg
    VECTORIZE_FLAGS = -ftree-vectorize -msse4.2

    # OpenMP detection for Clang
    OPENMP_TEST := $(shell echo 'int main(){return 0;}' | $(CC) -fopenmp -x c - -o /dev/null 2>/dev/null && echo "yes")
    ifeq ($(OPENMP_TEST),yes)
        OPENMP_FLAGS = -fopenmp
        OPENMP_LIBS = -fopenmp
    else
        OPENMP_TEST2 := $(shell echo 'int main(){return 0;}' | $(CC) -Xpreprocessor -fopenmp -lomp -x c - -o /dev/null 2>/dev/null && echo "yes")
        ifeq ($(OPENMP_TEST2),yes)
            OPENMP_FLAGS = -Xpreprocessor -fopenmp
            OPENMP_LIBS = -lomp
        else
            OPENMP_FLAGS =
            OPENMP_LIBS =
            OPENMP_DISABLED = 1
        endif
    endif
else ifneq (,$(findstring gcc,$(CC_TYPE)))
    # GCC
    CFLAGS = $(BASE_CFLAGS) -funroll-loops -fomit-frame-pointer
    CXXFLAGS = $(CFLAGS)
    NATIVE_FLAGS = -march=native -mtune=native
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -funroll-loops
    WALL_FLAGS = -Wall -Wextra
    DEBUG_FLAGS = -g -DDEBUG
    SANITIZER_FLAGS = -fsanitize=address -fno-omit-frame-pointer
    PROFILE_FLAGS = -pg
    VECTORIZE_FLAGS = -ftree-vectorize -msse4.2
    OPENMP_FLAGS = -fopenmp
    OPENMP_LIBS = -lgomp
else
    # Unknown compiler
    CFLAGS = $(BASE_CFLAGS)
    CXXFLAGS = $(CFLAGS)
    NATIVE_FLAGS =
    FAST_MATH =
    UNROLL_FLAGS =
    WALL_FLAGS = -Wall
    DEBUG_FLAGS = -g
    SANITIZER_FLAGS =
    PROFILE_FLAGS =
    VECTORIZE_FLAGS =
    OPENMP_FLAGS =
    OPENMP_LIBS =
    $(warning Warning: Unknown compiler, using conservative defaults)
endif

# Apply native optimizations by default (except NVCC)
ifndef USING_NVCC
    CFLAGS += $(NATIVE_FLAGS)
    CXXFLAGS += $(NATIVE_FLAGS)
endif

# Target executable
TARGET = lbm

# Source files for LBM simulation
C_SOURCES = main.c lbm.c
CPP_SOURCES =
SOURCES = $(C_SOURCES) $(CPP_SOURCES)

# Object files
C_OBJECTS = $(C_SOURCES:.c=.o)
CPP_OBJECTS = $(CPP_SOURCES:.cpp=.o)
OBJECTS = $(C_OBJECTS) $(CPP_OBJECTS)

# Header dependencies
HEADERS = main.h lbm.h lbm_1d_array.h config.h

# Default target
all: $(TARGET)

# Link the executable
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) $(LDFLAGS) $(LIBS) -o $(TARGET)
	@echo "Build complete: $(TARGET) ($(COMPILER_INFO))"
	@echo "Usage: ./$(TARGET) <timesteps> <result_file> <action> <sim_type> [obstacle_file]"

# Compile C source files
%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# Compile C++ source files
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET) *.dat *.out *.gcda *.gcno gmon.out *.ptx *.cubin
	@echo "Clean complete"

# Clean and rebuild
rebuild: clean all

# Compiler-specific targets
gcc:
	$(MAKE) CC=gcc CXX=g++

clang:
	$(MAKE) CC=clang CXX=clang++

nvcc:
	$(MAKE) CC=nvcc CXX=nvcc

# OpenMP enabled build
openmp:
ifdef OPENMP_DISABLED
	@echo "Error: OpenMP not available with $(COMPILER_INFO)"
	@echo "On macOS with clang, install OpenMP: brew install libomp"
	@false
else
	$(MAKE) CFLAGS="$(CFLAGS) $(OPENMP_FLAGS) -DOPENMP_ENABLED" \
	        CXXFLAGS="$(CXXFLAGS) $(OPENMP_FLAGS) -DOPENMP_ENABLED" \
	        LIBS="$(LIBS) $(OPENMP_LIBS)"
endif

# Debug build
debug:
ifdef USING_NVCC
	$(MAKE) CFLAGS="$(DEBUG_FLAGS)" CXXFLAGS="$(DEBUG_FLAGS)" LDFLAGS="-g"
else
	$(MAKE) CFLAGS="$(DEBUG_FLAGS) $(WALL_FLAGS)" CXXFLAGS="$(DEBUG_FLAGS) $(WALL_FLAGS)" LDFLAGS="-g"
endif

# Release build with maximum optimization
release:
ifdef USING_NVCC
	$(MAKE) CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG" \
	        CXXFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG"
else
	$(MAKE) CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) -fomit-frame-pointer $(NATIVE_FLAGS) $(FAST_MATH) -DNDEBUG" \
	        CXXFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) -fomit-frame-pointer $(NATIVE_FLAGS) $(FAST_MATH) -DNDEBUG"
endif

# Vectorization optimized build
vectorize:
ifndef USING_NVCC
	$(MAKE) CFLAGS="$(CFLAGS) $(VECTORIZE_FLAGS) $(FAST_MATH)" \
	        CXXFLAGS="$(CXXFLAGS) $(VECTORIZE_FLAGS) $(FAST_MATH)"
else
	@echo "Vectorization flags not applicable for NVCC"
	$(MAKE) nvcc
endif

# Fast math build
fast:
	$(MAKE) CFLAGS="$(CFLAGS) $(FAST_MATH)" CXXFLAGS="$(CXXFLAGS) $(FAST_MATH)"

# Large workload build
large:
	$(MAKE) CFLAGS="$(CFLAGS) -DLARGE_WORKLOAD" CXXFLAGS="$(CXXFLAGS) -DLARGE_WORKLOAD"

# Profile-guided optimization
pgo-generate: clean
ifndef USING_NVCC
	$(MAKE) CFLAGS="$(CFLAGS) -fprofile-generate" \
	        CXXFLAGS="$(CXXFLAGS) -fprofile-generate" \
	        LDFLAGS="$(LDFLAGS) -fprofile-generate"
else
	@echo "PGO not supported with NVCC"
	@false
endif

pgo-use: clean
ifndef USING_NVCC
	$(MAKE) CFLAGS="$(CFLAGS) -fprofile-use" \
	        CXXFLAGS="$(CXXFLAGS) -fprofile-use" \
	        LDFLAGS="$(LDFLAGS) -fprofile-use"
else
	@echo "PGO not supported with NVCC"
	@false
endif

# Memory debugging
asan:
ifndef USING_NVCC
	$(MAKE) CFLAGS="-g -O1 $(SANITIZER_FLAGS)" \
	        CXXFLAGS="-g -O1 $(SANITIZER_FLAGS)" \
	        LDFLAGS="-fsanitize=address"
else
	@echo "AddressSanitizer not supported with NVCC"
	@false
endif

# Thread debugging
tsan:
ifndef USING_NVCC
	$(MAKE) CFLAGS="-g -O1 -fsanitize=thread" \
	        CXXFLAGS="-g -O1 -fsanitize=thread" \
	        LDFLAGS="-fsanitize=thread"
else
	@echo "ThreadSanitizer not supported with NVCC"
	@false
endif

# Profiling build
profile:
ifndef USING_NVCC
	$(MAKE) CFLAGS="$(CFLAGS) $(PROFILE_FLAGS)" \
	        CXXFLAGS="$(CXXFLAGS) $(PROFILE_FLAGS)" \
	        LDFLAGS="$(LDFLAGS) $(PROFILE_FLAGS)"
else
	$(MAKE) CFLAGS="$(CFLAGS) $(PROFILE_FLAGS)" \
	        CXXFLAGS="$(CXXFLAGS) $(PROFILE_FLAGS)" \
	        LDFLAGS="$(LDFLAGS)"
endif

# CUDA-specific targets
cuda-debug:
ifdef USING_NVCC
	$(MAKE) CC=nvcc CXX=nvcc CFLAGS="$(DEBUG_FLAGS) $(ARCH_FLAGS)" CXXFLAGS="$(DEBUG_FLAGS) $(ARCH_FLAGS)"
else
	@echo "CUDA debug requires NVCC compiler"
	@false
endif

cuda-release:
ifdef USING_NVCC
	$(MAKE) CC=nvcc CXX=nvcc CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG" \
	                              CXXFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG"
else
	@echo "CUDA release requires NVCC compiler"
	@false
endif

# Show compiler information
compiler-info:
	@echo "LBM Compiler Detection Results:"
	@echo "  CC: $(CC)"
	@echo "  CXX: $(CXX)"
	@echo "  Compiler Info: $(COMPILER_INFO)"
	@echo "  CFLAGS: $(CFLAGS)"
	@echo "  CXXFLAGS: $(CXXFLAGS)"
	@echo "  LDFLAGS: $(LDFLAGS)"
	@echo "  LIBS: $(LIBS)"
ifdef USING_NVCC
	@echo "  CUDA Architecture: $(ARCH_FLAGS)"
endif
ifdef OPENMP_DISABLED
	@echo "  OpenMP: Disabled"
else
	@echo "  OpenMP Flags: $(OPENMP_FLAGS)"
	@echo "  OpenMP Libs: $(OPENMP_LIBS)"
endif

# Test targets
test: $(TARGET)
	@echo "Running LBM fluid dynamics tests with $(COMPILER_INFO)..."
	@echo "Test 1: Lid-driven cavity (100 timesteps)"
	./$(TARGET) 100 test_ldc.dat 2 0 || true
	@echo "Test 2: Channel flow (50 timesteps)"
	./$(TARGET) 50 test_channel.dat 2 1 || true
	@echo "Basic tests complete"

perf-test: $(TARGET)
	@echo "Running performance test (1000 timesteps) with $(COMPILER_INFO)..."
	time ./$(TARGET) 1000 perf_test.dat 2 0

large-test: large
	@echo "Running large workload test..."
	time ./$(TARGET) 500 large_test.dat 2 0

# Create sample obstacle file
create-obstacle:
	@echo "Creating sample obstacle file..."
	@python3 -c "import struct; SIZE_X, SIZE_Y, SIZE_Z = 100, 100, 130; f = open('sample_obstacle.dat', 'wb'); [f.write(b'X' if 20 <= x <= 80 and 20 <= y <= 80 and 40 <= z <= 90 and (x-50)**2 + (y-50)**2 < 400 else b'.') for z in range(SIZE_Z) for y in range(SIZE_Y) for x in range(SIZE_X)]; f.close()"
	@echo "Sample obstacle file created"

# Test with obstacle
test-obstacle: $(TARGET) create-obstacle
	@echo "Testing with obstacle geometry..."
	./$(TARGET) 100 test_obstacle.dat 2 1 sample_obstacle.dat

# Benchmark different optimization levels
benchmark:
	@echo "Benchmarking different optimization levels with $(COMPILER_INFO)..."
	@echo "Building O0 version..."
	@$(MAKE) CFLAGS="-O0" clean all > /dev/null 2>&1
	@echo "O0 timing:"
	@time ./$(TARGET) 100 bench_o0.dat 0 0 2>/dev/null || true
	@echo "Building O2 version..."
	@$(MAKE) CFLAGS="-O2" clean all > /dev/null 2>&1
	@echo "O2 timing:"
	@time ./$(TARGET) 100 bench_o2.dat 0 0 2>/dev/null || true
	@echo "Building O3 version..."
	@$(MAKE) CFLAGS="-O3 $(UNROLL_FLAGS) -fomit-frame-pointer" clean all > /dev/null 2>&1
	@echo "O3 timing:"
	@time ./$(TARGET) 100 bench_o3.dat 0 0 2>/dev/null || true

# Show help
help:
	@echo "LBM (Lattice Boltzmann Method) - Multi-Compiler Makefile"
	@echo "========================================================"
	@echo ""
	@echo "Supported Compilers:"
	@echo "  gcc/g++   - GNU Compiler Collection"
	@echo "  clang++   - LLVM Clang"
	@echo "  nvcc      - NVIDIA CUDA Compiler"
	@echo ""
	@echo "Basic Targets:"
	@echo "  all           - Build with default compiler"
	@echo "  clean         - Remove build artifacts"
	@echo "  rebuild       - Clean and build"
	@echo "  test          - Run basic simulation tests"
	@echo ""
	@echo "Compiler Selection:"
	@echo "  gcc           - Build with GCC"
	@echo "  clang         - Build with Clang"
	@echo "  nvcc          - Build with NVIDIA NVCC"
	@echo ""
	@echo "Build Variants:"
	@echo "  debug         - Debug build with symbols"
	@echo "  release       - Optimized release build"
	@echo "  fast          - Fast math optimizations"
	@echo "  large         - Large workload build"
	@echo "  openmp        - OpenMP parallel build"
	@echo "  vectorize     - Vectorization optimizations"
	@echo "  profile       - Profiling build"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Basic simulation tests"
	@echo "  perf-test     - Performance test (1000 timesteps)"
	@echo "  large-test    - Large workload test"
	@echo "  test-obstacle - Test with obstacle geometry"
	@echo "  benchmark     - Benchmark different optimization levels"
	@echo ""
	@echo "Analysis & Debugging:"
	@echo "  asan          - AddressSanitizer build"
	@echo "  tsan          - ThreadSanitizer build"
	@echo "  pgo-generate  - Profile-guided optimization step 1"
	@echo "  pgo-use       - Profile-guided optimization step 2"
	@echo ""
	@echo "CUDA-specific (NVCC only):"
	@echo "  cuda-debug    - CUDA debug build"
	@echo "  cuda-release  - CUDA optimized build"
	@echo ""
	@echo "Utilities:"
	@echo "  create-obstacle - Create sample obstacle file"
	@echo "  compiler-info   - Show compiler information"
	@echo "  help            - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make                    # Build with default compiler"
	@echo "  make CC=clang           # Build with Clang"
	@echo "  make nvcc openmp        # CUDA with OpenMP"
	@echo "  make gcc vectorize      # GCC with vectorization"

# Dependencies
main.o: main.c main.h lbm.h config.h
lbm.o: lbm.c lbm.h lbm_1d_array.h config.h

# Phony targets
.PHONY: all clean rebuild gcc clang nvcc openmp debug release vectorize fast large pgo-generate pgo-use asan tsan profile cuda-debug cuda-release compiler-info test perf-test large-test create-obstacle test-obstacle benchmark help
