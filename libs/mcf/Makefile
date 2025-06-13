# Makefile for cleaned MCF (Minimum Cost Flow) optimizer
# Original MCF optimizer restored from SPEC CPU2017 version
# Supports GCC, Clang, and NVCC

# Compiler selection (can be overridden: make CC=clang or make CC=nvcc)
CC ?= gcc

# Detect compiler type
COMPILER_NAME := $(notdir $(CC))
ifeq ($(COMPILER_NAME),nvcc)
    COMPILER_TYPE = nvcc
else
    COMPILER_TYPE := $(shell $(CC) --version 2>&1 | head -n1)
endif

# Base flags
BASE_CFLAGS = -O3
LDFLAGS =
LIBS = -lm

# Compiler-specific settings
ifeq ($(COMPILER_NAME),nvcc)
    # NVIDIA NVCC
    CFLAGS = $(BASE_CFLAGS) -Xcompiler -fomit-frame-pointer
    OPENMP_FLAGS = -Xcompiler -fopenmp
    OPENMP_LIBS = -lgomp
    ARCH_FLAGS = -arch=sm_35
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -Xcompiler -funroll-loops
    NATIVE_FLAGS =
    WALL_FLAGS = -Xcompiler -Wall,-Wextra
    DEBUG_FLAGS = -g -G -Xcompiler -DDEBUG,-DAT_HOME
    SANITIZER_FLAGS =
    PROFILE_FLAGS = -Xcompiler -pg
    COMPILER_INFO = "NVIDIA NVCC"
else ifneq (,$(findstring clang,$(COMPILER_TYPE)))
    # Clang
    CFLAGS = $(BASE_CFLAGS) -funroll-loops -fomit-frame-pointer
    NATIVE_FLAGS = -march=native -mtune=native
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -funroll-loops
    WALL_FLAGS = -Wall -Wextra
    DEBUG_FLAGS = -g -DDEBUG -DAT_HOME
    SANITIZER_FLAGS = -fsanitize=address -fno-omit-frame-pointer
    PROFILE_FLAGS = -pg
    COMPILER_INFO = "Clang"

    # OpenMP detection for Clang
    OPENMP_TEST := $(shell echo 'int main(){return 0;}' | $(CC) -fopenmp -x c - -o /dev/null 2>/dev/null && echo "yes")
    ifeq ($(OPENMP_TEST),yes)
        OPENMP_FLAGS = -fopenmp
        OPENMP_LIBS = -fopenmp
    else
        # Try libomp for clang (macOS)
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
else ifneq (,$(findstring gcc,$(COMPILER_TYPE)))
    # GCC
    CFLAGS = $(BASE_CFLAGS) -funroll-loops -fomit-frame-pointer
    NATIVE_FLAGS = -march=native -mtune=native
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -funroll-loops
    WALL_FLAGS = -Wall -Wextra
    DEBUG_FLAGS = -g -DDEBUG -DAT_HOME
    SANITIZER_FLAGS = -fsanitize=address -fno-omit-frame-pointer
    PROFILE_FLAGS = -pg
    OPENMP_FLAGS = -fopenmp
    OPENMP_LIBS = -lgomp
    COMPILER_INFO = "GCC"
else
    # Unknown compiler - use conservative defaults
    CFLAGS = $(BASE_CFLAGS)
    NATIVE_FLAGS =
    FAST_MATH =
    UNROLL_FLAGS =
    WALL_FLAGS = -Wall
    DEBUG_FLAGS = -g
    SANITIZER_FLAGS =
    PROFILE_FLAGS =
    OPENMP_FLAGS =
    OPENMP_LIBS =
    COMPILER_INFO = "Unknown Compiler"
    $(warning Warning: Unknown compiler $(CC), using conservative defaults)
endif

# Apply native optimizations by default (except for NVCC)
ifneq ($(COMPILER_NAME),nvcc)
    CFLAGS += $(NATIVE_FLAGS)
endif

# Target executable
TARGET = mcf

# Source files (all C files except SPEC-specific ones)
SOURCES = mcf.c \
          implicit.c \
          mcfutil.c \
          output.c \
          pbla.c \
          pbeampp.c \
          pflowup.c \
          pstart.c \
          psimplex.c \
          readmin.c \
          treeup.c

# Object files
OBJECTS = $(SOURCES:.c=.o)

# Header files
HEADERS = defines.h \
          implicit.h \
          mcf.h \
          mcfutil.h \
          mcflimit.h \
          output.h \
          pbla.h \
          pbeampp.h \
          pflowup.h \
          prototyp.h \
          pstart.h \
          psimplex.h \
          readmin.h \
          treeup.h

# Default target
all: $(TARGET)

# Link the executable
$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) $(LDFLAGS) $(LIBS) -o $(TARGET)
	@echo "Build complete: $(TARGET) ($(COMPILER_INFO))"

# Compile C source files
%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(TARGET) *.gcda *.gcno gmon.out *.ptx *.cubin
	@echo "Clean complete"

# Clean and rebuild
rebuild: clean all

# Compiler-specific targets
gcc:
	$(MAKE) CC=gcc

clang:
	$(MAKE) CC=clang

nvcc:
	$(MAKE) CC=nvcc

# OpenMP enabled build
openmp:
ifdef OPENMP_DISABLED
	@echo "Error: OpenMP not available with $(COMPILER_INFO)"
	@echo "On macOS with clang, install OpenMP: brew install libomp"
	@false
else
	$(MAKE) CFLAGS="$(CFLAGS) $(OPENMP_FLAGS)" LIBS="$(LIBS) $(OPENMP_LIBS)"
endif

# Debug build
debug:
ifeq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="$(DEBUG_FLAGS)" LDFLAGS="-g"
else
	$(MAKE) CFLAGS="$(DEBUG_FLAGS) $(WALL_FLAGS)" LDFLAGS="-g"
endif

# Release build with maximum optimization
release:
ifeq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG -DREPORT"
else
	$(MAKE) CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) -fomit-frame-pointer $(NATIVE_FLAGS) $(FAST_MATH) -DNDEBUG -DREPORT"
endif

# Fast math build
fast:
	$(MAKE) CFLAGS="$(CFLAGS) $(FAST_MATH)"

# Profile-guided optimization
pgo-generate: clean
ifneq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="$(CFLAGS) -fprofile-generate" LDFLAGS="$(LDFLAGS) -fprofile-generate"
else
	@echo "PGO not supported with NVCC"
	@false
endif

pgo-use: clean
ifneq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="$(CFLAGS) -fprofile-use" LDFLAGS="$(LDFLAGS) -fprofile-use"
else
	@echo "PGO not supported with NVCC"
	@false
endif

# Memory debugging (AddressSanitizer)
asan:
ifneq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="-g -O1 $(SANITIZER_FLAGS)" LDFLAGS="-fsanitize=address"
else
	@echo "AddressSanitizer not supported with NVCC"
	@false
endif

# Thread debugging (ThreadSanitizer)
tsan:
ifneq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="-g -O1 -fsanitize=thread" LDFLAGS="-fsanitize=thread"
else
	@echo "ThreadSanitizer not supported with NVCC"
	@false
endif

# Profiling build
profile:
ifneq ($(COMPILER_NAME),nvcc)
	$(MAKE) CFLAGS="$(CFLAGS) $(PROFILE_FLAGS)" LDFLAGS="$(LDFLAGS) $(PROFILE_FLAGS)"
else
	$(MAKE) CFLAGS="$(CFLAGS) $(PROFILE_FLAGS)" LDFLAGS="$(LDFLAGS)"
endif

# CUDA-specific targets (only for NVCC)
cuda-debug:
ifeq ($(COMPILER_NAME),nvcc)
	$(MAKE) CC=nvcc CFLAGS="$(DEBUG_FLAGS) $(ARCH_FLAGS)"
else
	@echo "CUDA debug target requires NVCC compiler"
	@false
endif

cuda-release:
ifeq ($(COMPILER_NAME),nvcc)
	$(MAKE) CC=nvcc CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG"
else
	@echo "CUDA release target requires NVCC compiler"
	@false
endif

# Show compiler information
compiler-info:
	@echo "Compiler Detection Results:"
	@echo "  CC: $(CC)"
	@echo "  Compiler Name: $(COMPILER_NAME)"
	@echo "  Compiler Type: $(COMPILER_INFO)"
	@echo "  CFLAGS: $(CFLAGS)"
	@echo "  LDFLAGS: $(LDFLAGS)"
	@echo "  LIBS: $(LIBS)"
ifeq ($(COMPILER_NAME),nvcc)
	@echo "  CUDA Architecture: $(ARCH_FLAGS)"
endif
ifdef OPENMP_DISABLED
	@echo "  OpenMP: Disabled"
else
	@echo "  OpenMP Flags: $(OPENMP_FLAGS)"
	@echo "  OpenMP Libs: $(OPENMP_LIBS)"
endif

# Test target
test: $(TARGET)
	@echo "Testing MCF optimizer with $(COMPILER_INFO)..."
	@if [ -f test.inp ]; then \
		./$(TARGET) test.inp; \
	else \
		echo "No test.inp file found. Run 'make create-test' first."; \
	fi

# Create sample test input
create-test:
	@echo "Creating sample test input file..."
	@echo "4 5" > test.inp
	@echo "1 10" >> test.inp
	@echo "2 20" >> test.inp
	@echo "3 30" >> test.inp
	@echo "4 40" >> test.inp
	@echo "1 2 5" >> test.inp
	@echo "2 3 3" >> test.inp
	@echo "3 4 4" >> test.inp
	@echo "1 3 8" >> test.inp
	@echo "2 4 6" >> test.inp
	@echo "Sample test.inp created"

# Benchmark
benchmark: $(TARGET)
	@echo "Running MCF benchmark with $(COMPILER_INFO)..."
	@if [ -f test.inp ]; then \
		time -p ./$(TARGET) test.inp; \
	else \
		echo "No test.inp found. Run 'make create-test' first."; \
	fi

# Show help
help:
	@echo "MCF (Minimum Cost Flow) Optimizer - Multi-Compiler Makefile"
	@echo "============================================================"
	@echo ""
	@echo "Supported Compilers:"
	@echo "  gcc    - GNU Compiler Collection"
	@echo "  clang  - LLVM Clang"
	@echo "  nvcc   - NVIDIA CUDA Compiler"
	@echo ""
	@echo "Basic Targets:"
	@echo "  all           - Build with default compiler ($(CC))"
	@echo "  clean         - Remove build artifacts"
	@echo "  rebuild       - Clean and build"
	@echo "  test          - Run basic tests"
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
	@echo "  openmp        - OpenMP parallel build"
	@echo "  profile       - Profiling build"
	@echo ""
	@echo "Analysis & Debugging:"
	@echo "  asan          - AddressSanitizer build (GCC/Clang only)"
	@echo "  tsan          - ThreadSanitizer build (GCC/Clang only)"
	@echo "  pgo-generate  - Profile-guided optimization step 1"
	@echo "  pgo-use       - Profile-guided optimization step 2"
	@echo ""
	@echo "CUDA-specific (NVCC only):"
	@echo "  cuda-debug    - CUDA debug build"
	@echo "  cuda-release  - CUDA optimized build"
	@echo ""
	@echo "Information:"
	@echo "  compiler-info - Show detected compiler information"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make                    # Build with default compiler"
	@echo "  make CC=clang           # Build with Clang"
	@echo "  make nvcc release       # CUDA optimized build"
	@echo "  make gcc openmp         # GCC with OpenMP"

# Dependencies
mcf.o: mcf.c mcf.h defines.h mcfutil.h readmin.h output.h pstart.h psimplex.h pbeampp.h implicit.h
implicit.o: implicit.c implicit.h mcfutil.h mcflimit.h defines.h prototyp.h
mcfutil.o: mcfutil.c mcfutil.h defines.h prototyp.h
output.o: output.c output.h mcfutil.h defines.h prototyp.h
pbla.o: pbla.c pbla.h defines.h prototyp.h
pbeampp.o: pbeampp.c pbeampp.h defines.h mcfutil.h prototyp.h
pflowup.o: pflowup.c pflowup.h defines.h prototyp.h
pstart.o: pstart.c pstart.h defines.h prototyp.h
psimplex.o: psimplex.c psimplex.h defines.h pbeampp.h pbla.h pflowup.h treeup.h mcfutil.h prototyp.h
readmin.o: readmin.c readmin.h defines.h mcfutil.h mcflimit.h prototyp.h
treeup.o: treeup.c treeup.h defines.h prototyp.h

# Phony targets
.PHONY: all clean rebuild gcc clang nvcc openmp debug release fast pgo-generate pgo-use asan tsan profile cuda-debug cuda-release compiler-info test create-test benchmark help
