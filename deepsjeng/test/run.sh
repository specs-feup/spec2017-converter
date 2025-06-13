#!/bin/bash

# Deep Sjeng Performance Benchmark Script
# Measures time and iterations to compare cleaned version vs original

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/benchmark_results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CLEANED_ENGINE="$SCRIPT_DIR/sjeng"
ORIGINAL_ENGINE=""  # Set this to path of original sjeng if available

# Benchmark configuration
DEFAULT_TIME_LIMIT=30  # seconds per test position
DEFAULT_ITERATIONS=3   # number of runs per test
VERBOSE=false
COMPARE_MODE=false

# Test suites
declare -A TEST_SUITES
TEST_SUITES[basic]="test.epd"
TEST_SUITES[tactical]="tactical.epd"
TEST_SUITES[endgame]="endgame.epd"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

# Function to show help
show_help() {
    cat << EOF
Deep Sjeng Performance Benchmark Script

Usage: $0 [options]

Options:
    -h, --help              Show this help message
    -t, --time SECONDS      Time limit per position (default: $DEFAULT_TIME_LIMIT)
    -i, --iterations NUM    Number of iterations per test (default: $DEFAULT_ITERATIONS)
    -o, --original PATH     Path to original sjeng executable for comparison
    -s, --suite NAME        Run specific test suite (basic, tactical, endgame, all)
    -v, --verbose           Verbose output
    -c, --clean             Clean previous benchmark results
    -r, --results           Show previous results

Test Suites:
    basic     - Basic positions from test.epd
    tactical  - Tactical puzzles (if tactical.epd exists)
    endgame   - Endgame positions (if endgame.epd exists)
    all       - All available test suites

Examples:
    $0                                    # Run basic benchmark
    $0 -t 60 -i 5                       # 60 seconds per position, 5 iterations
    $0 -o /path/to/original/sjeng -s all # Compare with original, all suites
    $0 -v -s tactical                    # Verbose output, tactical suite only

EOF
}

# Function to create test position files
create_test_files() {
    print_color $BLUE "Creating test position files..."

    # Enhanced basic test file
    cat > "$SCRIPT_DIR/test.epd" << 'EOF'
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1; bm e4; id "Starting Position";
r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3; bm d3; id "Italian Game";
rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3; bm Ng5; id "Italian vs Two Knights";
r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5; bm O-O; id "Italian Development";
rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 4 4; bm f4; id "King's Indian Attack";
EOF

    # Tactical test positions
    cat > "$SCRIPT_DIR/tactical.epd" << 'EOF'
r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4; bm Bc5; id "Tactical 1";
rnbqk1nr/pppp1ppp/8/2b1p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3; bm Qh5; id "Scholar's Mate Setup";
r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4; bm Ng5; id "Knight Attack";
rnbqkb1r/ppp2ppp/3p1n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 4; bm Bg5; id "Pin the Knight";
r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4; bm d3; id "Solid Development";
EOF

    # Endgame test positions
    cat > "$SCRIPT_DIR/endgame.epd" << 'EOF'
8/8/8/8/8/8/1k6/K7 w - - 0 1; bm Kb1; id "King and Pawn Endgame 1";
8/8/8/8/8/2k5/8/K7 w - - 0 1; bm Kb1; id "King Opposition";
8/8/8/3k4/8/8/8/3K4 w - - 0 1; bm Kd2; id "Central King";
8/8/8/8/8/8/3k4/3K4 w - - 0 1; bm Kd2; id "King Opposition 2";
8/8/8/8/3P4/8/3k4/3K4 w - - 0 1; bm d5; id "Pawn Push";
EOF

    print_color $GREEN "Test files created successfully."
}

# Function to check engine executable
check_engine() {
    local engine_path=$1
    local engine_name=$2

    if [ ! -f "$engine_path" ]; then
        print_color $RED "Error: $engine_name not found at $engine_path"
        return 1
    fi

    if [ ! -x "$engine_path" ]; then
        print_color $RED "Error: $engine_name is not executable"
        return 1
    fi

    return 0
}

# Function to run single benchmark
run_single_benchmark() {
    local engine_path=$1
    local engine_name=$2
    local epd_file=$3
    local time_limit=$4
    local iteration=$5

    print_color $YELLOW "Running $engine_name on $epd_file (iteration $iteration, ${time_limit}s per position)..."

    local start_time=$(date +%s.%N)
    local temp_output=$(mktemp)
    local position_count=0
    local nodes_total=0
    local nps_total=0

    # Count positions in EPD file
    position_count=$(grep -c "^[^#]" "$epd_file" 2>/dev/null || echo "0")

    if [ "$position_count" -eq 0 ]; then
        print_color $RED "Warning: No valid positions found in $epd_file"
        rm -f "$temp_output"
        return 1
    fi

    # Run the engine with timeout
    cd "$SCRIPT_DIR"
    timeout $((time_limit * position_count + 10)) "$engine_path" "$epd_file" > "$temp_output" 2>&1
    local exit_code=$?

    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0")

    # Parse output for nodes and NPS if available
    if [ -f "$temp_output" ]; then
        # Try to extract nodes and NPS from output
        nodes_total=$(grep -i "nodes" "$temp_output" | tail -1 | grep -o '[0-9]\+' | head -1 || echo "0")
        nps_total=$(grep -i "nps\|nodes/sec" "$temp_output" | tail -1 | grep -o '[0-9]\+' | head -1 || echo "0")

        if [ "$VERBOSE" = true ]; then
            echo "Engine output preview:"
            head -10 "$temp_output"
            echo "..."
            tail -5 "$temp_output"
        fi
    fi

    # Calculate average time per position
    local avg_time_per_pos=$(echo "scale=3; $total_time / $position_count" | bc -l 2>/dev/null || echo "0")

    echo "$engine_name,$epd_file,$iteration,$position_count,$total_time,$avg_time_per_pos,$nodes_total,$nps_total,$exit_code"

    rm -f "$temp_output"
    return 0
}

# Function to run benchmark suite
run_benchmark_suite() {
    local suite_name=$1
    local epd_file=$2
    local time_limit=$3
    local iterations=$4

    print_color $BLUE "=== Running benchmark suite: $suite_name ==="

    if [ ! -f "$epd_file" ]; then
        print_color $RED "Error: EPD file not found: $epd_file"
        return 1
    fi

    local results_file="$RESULTS_DIR/benchmark_${suite_name}_${TIMESTAMP}.csv"

    # Create CSV header
    echo "Engine,EPD_File,Iteration,Positions,Total_Time,Avg_Time_Per_Pos,Nodes,NPS,Exit_Code" > "$results_file"

    # Run cleaned engine
    print_color $GREEN "Testing cleaned Deep Sjeng..."
    for i in $(seq 1 $iterations); do
        run_single_benchmark "$CLEANED_ENGINE" "Cleaned_Sjeng" "$epd_file" "$time_limit" "$i" >> "$results_file"
    done

    # Run original engine if available
    if [ "$COMPARE_MODE" = true ] && [ -n "$ORIGINAL_ENGINE" ]; then
        print_color $GREEN "Testing original Deep Sjeng..."
        for i in $(seq 1 $iterations); do
            run_single_benchmark "$ORIGINAL_ENGINE" "Original_Sjeng" "$epd_file" "$time_limit" "$i" >> "$results_file"
        done
    fi

    print_color $GREEN "Results saved to: $results_file"

    # Generate summary
    generate_summary "$results_file" "$suite_name"
}

# Function to generate benchmark summary
generate_summary() {
    local results_file=$1
    local suite_name=$2

    print_color $BLUE "=== Benchmark Summary: $suite_name ==="

    if [ ! -f "$results_file" ]; then
        print_color $RED "Results file not found: $results_file"
        return 1
    fi

    # Calculate averages for cleaned engine
    local cleaned_avg_time=$(awk -F',' 'NR>1 && $1=="Cleaned_Sjeng" {sum+=$5; count++} END {if(count>0) printf "%.3f", sum/count; else print "0"}' "$results_file")
    local cleaned_avg_per_pos=$(awk -F',' 'NR>1 && $1=="Cleaned_Sjeng" {sum+=$6; count++} END {if(count>0) printf "%.3f", sum/count; else print "0"}' "$results_file")
    local cleaned_avg_nodes=$(awk -F',' 'NR>1 && $1=="Cleaned_Sjeng" {sum+=$7; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}' "$results_file")
    local cleaned_avg_nps=$(awk -F',' 'NR>1 && $1=="Cleaned_Sjeng" {sum+=$8; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}' "$results_file")

    echo "Cleaned Deep Sjeng Performance:"
    echo "  Average total time: ${cleaned_avg_time}s"
    echo "  Average time per position: ${cleaned_avg_per_pos}s"
    echo "  Average nodes searched: $cleaned_avg_nodes"
    echo "  Average NPS: $cleaned_avg_nps"

    # Compare with original if available
    if [ "$COMPARE_MODE" = true ] && grep -q "Original_Sjeng" "$results_file"; then
        local original_avg_time=$(awk -F',' 'NR>1 && $1=="Original_Sjeng" {sum+=$5; count++} END {if(count>0) printf "%.3f", sum/count; else print "0"}' "$results_file")
        local original_avg_per_pos=$(awk -F',' 'NR>1 && $1=="Original_Sjeng" {sum+=$6; count++} END {if(count>0) printf "%.3f", sum/count; else print "0"}' "$results_file")
        local original_avg_nodes=$(awk -F',' 'NR>1 && $1=="Original_Sjeng" {sum+=$7; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}' "$results_file")
        local original_avg_nps=$(awk -F',' 'NR>1 && $1=="Original_Sjeng" {sum+=$8; count++} END {if(count>0) printf "%.0f", sum/count; else print "0"}' "$results_file")

        echo ""
        echo "Original Deep Sjeng Performance:"
        echo "  Average total time: ${original_avg_time}s"
        echo "  Average time per position: ${original_avg_per_pos}s"
        echo "  Average nodes searched: $original_avg_nodes"
        echo "  Average NPS: $original_avg_nps"

        echo ""
        echo "Performance Comparison (Cleaned vs Original):"

        # Calculate percentage differences
        if [ "$original_avg_time" != "0" ]; then
            local time_diff=$(echo "scale=2; (($cleaned_avg_time - $original_avg_time) / $original_avg_time) * 100" | bc -l 2>/dev/null || echo "N/A")
            echo "  Time difference: ${time_diff}%"
        fi

        if [ "$original_avg_nodes" != "0" ]; then
            local nodes_diff=$(echo "scale=2; (($cleaned_avg_nodes - $original_avg_nodes) / $original_avg_nodes) * 100" | bc -l 2>/dev/null || echo "N/A")
            echo "  Nodes difference: ${nodes_diff}%"
        fi

        if [ "$original_avg_nps" != "0" ]; then
            local nps_diff=$(echo "scale=2; (($cleaned_avg_nps - $original_avg_nps) / $original_avg_nps) * 100" | bc -l 2>/dev/null || echo "N/A")
            echo "  NPS difference: ${nps_diff}%"
        fi
    fi

    echo ""
}

# Function to show previous results
show_results() {
    print_color $BLUE "=== Previous Benchmark Results ==="

    if [ ! -d "$RESULTS_DIR" ]; then
        print_color $YELLOW "No previous results found."
        return 0
    fi

    local csv_files=$(find "$RESULTS_DIR" -name "*.csv" -type f 2>/dev/null | sort)

    if [ -z "$csv_files" ]; then
        print_color $YELLOW "No CSV result files found."
        return 0
    fi

    echo "Available result files:"
    echo "$csv_files" | nl -w2 -s'. '

    echo ""
    echo "Latest results:"
    local latest=$(echo "$csv_files" | tail -1)
    if [ -f "$latest" ]; then
        echo "File: $(basename "$latest")"
        echo "Contents:"
        head -10 "$latest"
        if [ $(wc -l < "$latest") -gt 10 ]; then
            echo "... (showing first 10 lines)"
        fi
    fi
}

# Function to clean previous results
clean_results() {
    if [ -d "$RESULTS_DIR" ]; then
        print_color $YELLOW "Removing previous benchmark results..."
        rm -rf "$RESULTS_DIR"
        print_color $GREEN "Previous results cleaned."
    else
        print_color $YELLOW "No previous results to clean."
    fi
}

# Main execution
main() {
    # Create results directory
    mkdir -p "$RESULTS_DIR"

    # Parse command line arguments
    TIME_LIMIT=$DEFAULT_TIME_LIMIT
    ITERATIONS=$DEFAULT_ITERATIONS
    SUITE="basic"

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--time)
                TIME_LIMIT="$2"
                shift 2
                ;;
            -i|--iterations)
                ITERATIONS="$2"
                shift 2
                ;;
            -o|--original)
                ORIGINAL_ENGINE="$2"
                COMPARE_MODE=true
                shift 2
                ;;
            -s|--suite)
                SUITE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--clean)
                clean_results
                exit 0
                ;;
            -r|--results)
                show_results
                exit 0
                ;;
            *)
                print_color $RED "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate inputs
    if ! [[ "$TIME_LIMIT" =~ ^[0-9]+$ ]] || [ "$TIME_LIMIT" -lt 1 ]; then
        print_color $RED "Error: Time limit must be a positive integer"
        exit 1
    fi

    if ! [[ "$ITERATIONS" =~ ^[0-9]+$ ]] || [ "$ITERATIONS" -lt 1 ]; then
        print_color $RED "Error: Iterations must be a positive integer"
        exit 1
    fi

    # Check engines
    if ! check_engine "$CLEANED_ENGINE" "Cleaned Deep Sjeng"; then
        print_color $RED "Please build the cleaned sjeng executable first: make"
        exit 1
    fi

    if [ "$COMPARE_MODE" = true ]; then
        if ! check_engine "$ORIGINAL_ENGINE" "Original Deep Sjeng"; then
            print_color $RED "Original engine not found or not executable: $ORIGINAL_ENGINE"
            exit 1
        fi
    fi

    # Create test files
    create_test_files

    # Print configuration
    print_color $BLUE "=== Benchmark Configuration ==="
    echo "Time limit per position: ${TIME_LIMIT}s"
    echo "Iterations per test: $ITERATIONS"
    echo "Test suite: $SUITE"
    echo "Cleaned engine: $CLEANED_ENGINE"
    if [ "$COMPARE_MODE" = true ]; then
        echo "Original engine: $ORIGINAL_ENGINE"
        echo "Comparison mode: enabled"
    else
        echo "Comparison mode: disabled"
    fi
    echo "Results directory: $RESULTS_DIR"
    echo ""

    # Run benchmarks
    case "$SUITE" in
        basic)
            run_benchmark_suite "basic" "$SCRIPT_DIR/test.epd" "$TIME_LIMIT" "$ITERATIONS"
            ;;
        tactical)
            run_benchmark_suite "tactical" "$SCRIPT_DIR/tactical.epd" "$TIME_LIMIT" "$ITERATIONS"
            ;;
        endgame)
            run_benchmark_suite "endgame" "$SCRIPT_DIR/endgame.epd" "$TIME_LIMIT" "$ITERATIONS"
            ;;
        all)
            run_benchmark_suite "basic" "$SCRIPT_DIR/test.epd" "$TIME_LIMIT" "$ITERATIONS"
            run_benchmark_suite "tactical" "$SCRIPT_DIR/tactical.epd" "$TIME_LIMIT" "$ITERATIONS"
            run_benchmark_suite "endgame" "$SCRIPT_DIR/endgame.epd" "$TIME_LIMIT" "$ITERATIONS"
            ;;
        *)
            print_color $RED "Unknown test suite: $SUITE"
            print_color $YELLOW "Available suites: basic, tactical, endgame, all"
            exit 1
            ;;
    esac

    print_color $GREEN "Benchmark completed successfully!"
    echo "Results saved in: $RESULTS_DIR"
}

# Check for required tools
for tool in bc timeout awk grep; do
    if ! command -v $tool >/dev/null 2>&1; then
        print_color $RED "Error: Required tool '$tool' not found"
        exit 1
    fi
done

# Run main function
main "$@"
