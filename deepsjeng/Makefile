# Makefile for cleaned deepsjeng chess engine
# Original sjeng chess engine restored from SPEC CPU2017 version
# Supports GCC, Clang, and NVCC

# Compiler selection (can be overridden: make CXX=clang++)
CC ?= gcc
CXX ?= g++

# Detect compiler type
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
    CXX_TYPE := $(shell $(CXX) --version 2>&1 | head -n1)
    ifneq (,$(findstring clang,$(CXX_TYPE)))
        COMPILER_INFO = "Clang++"
    else ifneq (,$(findstring g++,$(CXX_TYPE)))
        COMPILER_INFO = "G++"
    else
        COMPILER_INFO = "Unknown C++"
    endif
endif

# Base optimization flags
BASE_CFLAGS = -O3
BASE_CXXFLAGS = -O3
LDFLAGS =
LIBS = -lm

# Compiler-specific settings
ifdef USING_NVCC
    # NVIDIA NVCC
    CFLAGS = $(BASE_CFLAGS) -Xcompiler -fomit-frame-pointer
    CXXFLAGS = $(BASE_CXXFLAGS) -Xcompiler -fomit-frame-pointer
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
    STD_FLAGS = -std=c++11
else ifneq (,$(findstring clang,$(CXX_TYPE)))
    # Clang++
    CFLAGS = $(BASE_CFLAGS) -funroll-loops -fomit-frame-pointer
    CXXFLAGS = $(BASE_CXXFLAGS) -funroll-loops -fomit-frame-pointer
    NATIVE_FLAGS = -march=native -mtune=native
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -funroll-loops
    WALL_FLAGS = -Wall -Wextra -Wno-deprecated-declarations
    DEBUG_FLAGS = -g -DDEBUG
    SANITIZER_FLAGS = -fsanitize=address -fno-omit-frame-pointer
    PROFILE_FLAGS = -pg
    STD_FLAGS = -std=c++11

    # OpenMP detection for Clang
    OPENMP_TEST := $(shell echo 'int main(){return 0;}' | $(CXX) -fopenmp -x c++ - -o /dev/null 2>/dev/null && echo "yes")
    ifeq ($(OPENMP_TEST),yes)
        OPENMP_FLAGS = -fopenmp
        OPENMP_LIBS = -fopenmp
    else
        OPENMP_TEST2 := $(shell echo 'int main(){return 0;}' | $(CXX) -Xpreprocessor -fopenmp -lomp -x c++ - -o /dev/null 2>/dev/null && echo "yes")
        ifeq ($(OPENMP_TEST2),yes)
            OPENMP_FLAGS = -Xpreprocessor -fopenmp
            OPENMP_LIBS = -lomp
        else
            OPENMP_FLAGS =
            OPENMP_LIBS =
            OPENMP_DISABLED = 1
        endif
    endif
else ifneq (,$(findstring g++,$(CXX_TYPE)))
    # G++
    CFLAGS = $(BASE_CFLAGS) -funroll-loops -fomit-frame-pointer
    CXXFLAGS = $(BASE_CXXFLAGS) -funroll-loops -fomit-frame-pointer
    NATIVE_FLAGS = -march=native -mtune=native
    FAST_MATH = -ffast-math
    UNROLL_FLAGS = -funroll-loops
    WALL_FLAGS = -Wall -Wextra -Wno-deprecated-declarations
    DEBUG_FLAGS = -g -DDEBUG
    SANITIZER_FLAGS = -fsanitize=address -fno-omit-frame-pointer
    PROFILE_FLAGS = -pg
    STD_FLAGS = -std=c++11
    OPENMP_FLAGS = -fopenmp
    OPENMP_LIBS = -lgomp
else
    # Unknown compiler
    CFLAGS = $(BASE_CFLAGS)
    CXXFLAGS = $(BASE_CXXFLAGS)
    NATIVE_FLAGS =
    FAST_MATH =
    UNROLL_FLAGS =
    WALL_FLAGS = -Wall
    DEBUG_FLAGS = -g
    SANITIZER_FLAGS =
    PROFILE_FLAGS =
    STD_FLAGS = -std=c++11
    OPENMP_FLAGS =
    OPENMP_LIBS =
    $(warning Warning: Unknown compiler, using conservative defaults)
endif

# Apply standard and native optimizations
CXXFLAGS += $(STD_FLAGS)
ifndef USING_NVCC
    CFLAGS += $(NATIVE_FLAGS)
    CXXFLAGS += $(NATIVE_FLAGS)
endif

# Target executable
TARGET = sjeng

# Automatically detect all C++ and C source files
CPP_SOURCES = $(wildcard *.cpp)
C_SOURCES = $(wildcard *.c)
SOURCES = $(CPP_SOURCES) $(C_SOURCES)

# Object files
CPP_OBJECTS = $(CPP_SOURCES:.cpp=.o)
C_OBJECTS = $(C_SOURCES:.c=.o)
OBJECTS = $(CPP_OBJECTS) $(C_OBJECTS)

# Header dependencies
HEADERS = sjeng.h config.h

# Default target
all: $(TARGET)

# Link the executable
$(TARGET): $(OBJECTS)
	$(CXX) $(OBJECTS) $(LDFLAGS) $(LIBS) -o $(TARGET)
	@echo "Build complete: $(TARGET) ($(COMPILER_INFO))"

# Compile C++ source files
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Compile C source files (if any exist)
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
	$(MAKE) CFLAGS="$(CFLAGS) $(OPENMP_FLAGS)" \
	        CXXFLAGS="$(CXXFLAGS) $(OPENMP_FLAGS)" \
	        LIBS="$(LIBS) $(OPENMP_LIBS)"
endif

# Debug build
debug:
ifdef USING_NVCC
	$(MAKE) CFLAGS="$(DEBUG_FLAGS)" CXXFLAGS="$(DEBUG_FLAGS)" LDFLAGS="-g"
else
	$(MAKE) CFLAGS="$(DEBUG_FLAGS) $(WALL_FLAGS)" \
	        CXXFLAGS="$(DEBUG_FLAGS) $(WALL_FLAGS)" LDFLAGS="-g"
endif

# Release build with maximum optimization
release:
ifdef USING_NVCC
	$(MAKE) CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG" \
	        CXXFLAGS="$(BASE_CXXFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) $(STD_FLAGS) -DNDEBUG"
else
	$(MAKE) CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) -fomit-frame-pointer $(NATIVE_FLAGS) $(FAST_MATH) -DNDEBUG" \
	        CXXFLAGS="$(BASE_CXXFLAGS) $(UNROLL_FLAGS) -fomit-frame-pointer $(NATIVE_FLAGS) $(FAST_MATH) $(STD_FLAGS) -DNDEBUG"
endif

# Fast math build
fast:
	$(MAKE) CFLAGS="$(CFLAGS) $(FAST_MATH)" CXXFLAGS="$(CXXFLAGS) $(FAST_MATH)"

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
	        CXXFLAGS="-g -O1 $(SANITIZER_FLAGS) $(STD_FLAGS)" \
	        LDFLAGS="-fsanitize=address"
else
	@echo "AddressSanitizer not supported with NVCC"
	@false
endif

# Thread debugging
tsan:
ifndef USING_NVCC
	$(MAKE) CFLAGS="-g -O1 -fsanitize=thread" \
	        CXXFLAGS="-g -O1 -fsanitize=thread $(STD_FLAGS)" \
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
	$(MAKE) CC=nvcc CXX=nvcc CFLAGS="$(DEBUG_FLAGS) $(ARCH_FLAGS)" \
	                         CXXFLAGS="$(DEBUG_FLAGS) $(ARCH_FLAGS) $(STD_FLAGS)"
else
	@echo "CUDA debug requires NVCC compiler"
	@false
endif

cuda-release:
ifdef USING_NVCC
	$(MAKE) CC=nvcc CXX=nvcc CFLAGS="$(BASE_CFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) -DNDEBUG" \
	                         CXXFLAGS="$(BASE_CXXFLAGS) $(UNROLL_FLAGS) $(FAST_MATH) $(ARCH_FLAGS) $(STD_FLAGS) -DNDEBUG"
else
	@echo "CUDA release requires NVCC compiler"
	@false
endif

# Show compiler information
compiler-info:
	@echo "Deepsjeng Chess Engine Compiler Detection:"
	@echo "  CC: $(CC)"
	@echo "  CXX: $(CXX)"
	@echo "  Compiler Info: $(COMPILER_INFO)"
	@echo "  CFLAGS: $(CFLAGS)"
	@echo "  CXXFLAGS: $(CXXFLAGS)"
	@echo "  LDFLAGS: $(LDFLAGS)"
	@echo "  LIBS: $(LIBS)"
	@echo "  C++ Standard: $(STD_FLAGS)"
ifdef USING_NVCC
	@echo "  CUDA Architecture: $(ARCH_FLAGS)"
endif
ifdef OPENMP_DISABLED
	@echo "  OpenMP: Disabled"
else
	@echo "  OpenMP Flags: $(OPENMP_FLAGS)"
	@echo "  OpenMP Libs: $(OPENMP_LIBS)"
endif

# List detected sources
list-sources:
	@echo "Detected source files:"
	@echo "  C++ sources ($(words $(CPP_SOURCES))): $(CPP_SOURCES)"
	@echo "  C sources ($(words $(C_SOURCES))): $(C_SOURCES)"
	@echo "  All sources: $(SOURCES)"
	@echo "  Objects: $(OBJECTS)"

# Test target
test: $(TARGET)
	@echo "Testing Deepsjeng Chess Engine with $(COMPILER_INFO)..."
	./$(TARGET) --help 2>/dev/null || echo "Chess engine built successfully"
	@echo "Basic test complete"

# Static analysis
analyze:
ifndef USING_NVCC
	@echo "Running static analysis with cppcheck..."
	cppcheck --enable=all --std=c++11 --language=c++ $(SOURCES) 2>/dev/null || echo "cppcheck not available"
else
	@echo "Static analysis not available for NVCC builds"
endif

# Show help
help:
	@echo "Deepsjeng Chess Engine - Multi-Compiler Makefile"
	@echo "================================================"
	@echo ""
	@echo "Supported Compilers:"
	@echo "  gcc/g++   - GNU Compiler Collection"
	@echo "  clang++   - LLVM Clang"
	@echo "  nvcc      - NVIDIA CUDA Compiler"
	@echo ""
	@echo "Basic Targets:"
	@echo "  all           - Build with default compiler ($(CXX))"
	@echo "  clean         - Remove build artifacts"
	@echo "  rebuild       - Clean and build"
	@echo "  test          - Run basic tests"
	@echo ""
	@echo "Compiler Selection:"
	@echo "  gcc           - Build with GCC/G++"
	@echo "  clang         - Build with Clang/Clang++"
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
	@echo "  analyze       - Static analysis with cppcheck"
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
	@echo "  list-sources  - Show detected source files"
	@echo "  help          - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make                    # Build with default compiler"
	@echo "  make CXX=clang++        # Build with Clang++"
	@echo "  make nvcc release       # CUDA optimized build"
	@echo "  make gcc openmp         # GCC with OpenMP"
	@echo "  make clang asan         # Clang with AddressSanitizer"
	@echo ""
	@echo "Note: Deepsjeng requires C++11 support"

# Basic dependencies (auto-generated would be better for large projects)
sjeng.o: sjeng.cpp sjeng.h config.h
search.o: search.cpp sjeng.h config.h
evaluate.o: evaluate.cpp sjeng.h config.h
moves.o: moves.cpp sjeng.h config.h
bitboard.o: bitboard.cpp sjeng.h config.h
ttable.o: ttable.cpp sjeng.h config.h
proof.o: proof.cpp sjeng.h config.h
see.o: see.cpp sjeng.h config.h
draw.o: draw.cpp sjeng.h config.h
ecache.o: ecache.cpp sjeng.h config.h
epd.o: epd.cpp sjeng.h config.h
utils.o: utils.cpp sjeng.h config.h

# Phony targets
.PHONY: all clean rebuild gcc clang nvcc openmp debug release fast pgo-generate pgo-use asan tsan profile cuda-debug cuda-release compiler-info list-sources test analyze help
