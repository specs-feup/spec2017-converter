# Compiler and flags
CXX = g++
CXXFLAGS = -Wall -O2 -std=c++17

# List all source files
# Example SRCS line:
SRCS = main.C Compute.C ComputeList.C PatchList.C Molecule.C LJTable.C SimParameters.C ResultSet.C ComputeNonbondedUtil.C \
       ComputeNonbondedStd.C ComputeNonbondedLES.C ComputeNonbondedFEP.C ComputeNonbondedPProf.C erf.C Patch.C


# Object files
OBJS = $(SRCS:.C=.o)

# Output binary
OUT = sim_benchmark

# Default rule
all: $(OUT)

# Link all object files into final binary
$(OUT): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Compile each .C file into .o
%.o: %.C
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Run with args
run: $(OUT)
	./$(OUT) $(ARGS)

# Clean up
clean:
	rm -f $(OUT) $(OBJS)