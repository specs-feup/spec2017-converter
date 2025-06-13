#!/usr/bin/env python3
"""
SPEC Proprietary Code Remover for Sjeng Chess Engine (Fixed Version)

This script removes SPEC-specific modifications from the Sjeng chess engine source code,
restoring it closer to the original open-source version.

Usage:
    python spec_cleaner.py input_file.c output_file.c
    python spec_cleaner.py input_directory/ output_directory/
"""

import re
import os
import sys
import argparse
from pathlib import Path
import shutil

class SpecCodeCleaner:
    def __init__(self):
        # Patterns to identify and clean SPEC-specific code
        self.patterns = {
            # Remove SPEC conditional compilation for const qualifiers
            'const_conditional': {
                'pattern': r'#if !defined\(SPEC\)\s*\nconst\s*\n#endif\s*\n',
                'replacement': 'const ',
                'description': 'Restore const qualifiers'
            },

            # Remove SPEC version strings
            'version_spec': {
                'pattern': r'#define VERSION "([^"]*)\s+SPEC"',
                'replacement': r'#define VERSION "\1"',
                'description': 'Remove SPEC from version string'
            },

            # Remove SPEC package name modifications
            'package_spec': {
                'pattern': r'#define PACKAGE "([^"]*)\s+SPEC"',
                'replacement': r'#define PACKAGE "\1"',
                'description': 'Remove SPEC from package name'
            },

            # Remove SPEC-specific function declarations
            'spec_function_decl': {
                'pattern': r'#if !defined\(SPEC\)\s*\n([^#]*?)\n#else\s*\n([^#]*?)\n#endif',
                'replacement': r'\1',
                'description': 'Use non-SPEC function declarations'
            },

            # Remove SPEC ifdefs around single statements
            'spec_ifdef_block': {
                'pattern': r'#if defined\(SPEC\)\s*\n(.*?)\n#else\s*\n(.*?)\n#endif',
                'replacement': r'\2',
                'description': 'Use non-SPEC code blocks'
            },

            # Remove standalone SPEC conditionals
            'spec_standalone': {
                'pattern': r'#ifdef SPEC\s*\n.*?\n#endif\s*\n',
                'replacement': '',
                'description': 'Remove SPEC-only code blocks'
            },

            # Clean up SPEC comments
            'spec_comments': {
                'pattern': r'/\*.*?SPEC.*?\*/',
                'replacement': '',
                'description': 'Remove SPEC-related comments'
            },

            # Remove SPEC configuration defines
            'spec_defines': {
                'pattern': r'#define\s+.*SPEC.*\n',
                'replacement': '',
                'description': 'Remove SPEC defines'
            },

            # Remove SPEC memory configuration blocks
            'spec_memory_config': {
                'pattern': r'#ifdef SMALL_MEMORY\s*\n.*?\n#elif BIG_MEMORY\s*\n.*?\n#else\s*\n#error Need to specify SMALL_MEMORY or BIG_MEMORY\.\s*\n#endif',
                'replacement': 'TTSize = 15000000; // Default hash size',
                'description': 'Replace SPEC memory configuration with default'
            },

            # Remove SPEC copyright protection blocks
            'spec_copyprotection': {
                'pattern': r'#if !defined COPYPROTECTION\s*\n(.*?)\n#endif',
                'replacement': r'\1',
                'description': 'Remove copy protection conditional compilation'
            },

            # Remove SPEC commandline handling
            'spec_commandline': {
                'pattern': r'/\* SPEC version: take EPD testset from commandline \*/\s*\n\s*if \(argc == 2\) \{\s*\n\s*run_epd_testsuite\(&gamestate, &state, argv\[1\]\);\s*\n\s*\} else \{\s*\n\s*myprintf\("Please specify the workfile\\n"\);\s*\n\s*return EXIT_FAILURE;\s*\n\s*\}',
                'replacement': '/* Normal UCI/XBoard interface would go here */',
                'description': 'Remove SPEC-specific EPD testset command line handling'
            },

            # Remove SPEC MAX_CPU limitations
            'spec_max_cpu': {
                'pattern': r'static pawntt_t PawnTT\[MAX_CPU\]\[1 << PAWN_HASH_LOG\];',
                'replacement': 'static pawntt_t PawnTT[1][1 << PAWN_HASH_LOG];',
                'description': 'Remove multi-CPU SPEC limitations'
            },

            # Remove SPEC thread restrictions
            'spec_thread_restrictions': {
                'pattern': r'int history_h\[MAX_CPU\]\[12\]\[64\];\s*\nint history_hit\[MAX_CPU\]\[12\]\[64\];\s*\nint history_tot\[MAX_CPU\]\[12\]\[64\];',
                'replacement': 'int history_h[1][12][64];\nint history_hit[1][12][64];\nint history_tot[1][12][64];',
                'description': 'Remove SPEC multi-threading restrictions'
            },

            # Restore normal UCI mode behavior
            'spec_uci_mode': {
                'pattern': r'uci_mode = FALSE;',
                'replacement': 'uci_mode = TRUE;',
                'description': 'Enable UCI mode by default'
            },

            # Remove SPEC-specific phase detection
            'spec_phase_detection': {
                'pattern': r'/\* quadratic scaling y = -0,0039x2 \+ 0,9954x \+ 13,2572 \*/',
                'replacement': '/* Standard king safety scaling */',
                'description': 'Remove SPEC-specific evaluation scaling comment'
            },

            # Remove SPEC zobrist hash generation - simpler approach
            'spec_zobrist_temp_var': {
                'pattern': r'#if defined\(SPEC\)\s*\n\s*BITBOARD temp;\s*\n#endif',
                'replacement': '',
                'description': 'Remove SPEC temp variable declaration'
            },

            'spec_zobrist_assignment': {
                'pattern': r'#if defined\(SPEC\)\s*\n\s*temp = \(\(BITBOARD\)myrandom\(\)\) << 32;\s*\n\s*temp \+= \(BITBOARD\)myrandom\(\);\s*\n\s*zobrist\[p\]\[q\] = temp;\s*\n#else\s*\n\s*zobrist\[p\]\[q\] = \(\(\(BITBOARD\)myrandom\(\)\) << 32\) \+ \(BITBOARD\)myrandom\(\);\s*\n#endif',
                'replacement': '            zobrist[p][q] = (((BITBOARD)myrandom()) << 32) + (BITBOARD)myrandom();',
                'description': 'Use non-SPEC zobrist hash generation'
            },

            # Remove SPEC Windows detection
            'spec_windows_detection': {
                'pattern': r'#if defined\(WIN32\) \|\| defined\(WIN64\) \|\| defined\(SPEC_WINDOWS\)',
                'replacement': '#if defined(WIN32) || defined(WIN64)',
                'description': 'Remove SPEC_WINDOWS detection'
            },

            # Remove SPEC logging conditionals
            'spec_logging_conditional': {
                'pattern': r'#if !defined COPYPROTECTION\s*\n(.*?)\n#endif',
                'replacement': r'\1',
                'description': 'Remove copy protection conditional compilation'
            },

            # Remove this pattern entirely - it's causing issues
            # 'spec_threadid_references': {
            #     'pattern': r's->threadid',
            #     'replacement': '0',
            #     'description': 'Replace SPEC threadid with single thread'
            # },

            # Pattern for any remaining MAX_CPU arrays
            'spec_max_cpu_arrays': {
                'pattern': r'\[MAX_CPU\]',
                'replacement': '[1]',
                'description': 'Replace MAX_CPU array dimensions with single element'
            },

            # Pattern for SPEC benchmark identification
            'spec_benchmark_comments': {
                'pattern': r'/\*.*SPEC.*benchmark.*\*/',
                'replacement': '',
                'description': 'Remove SPEC benchmark identification comments'
            },

            # Remove SPEC-specific CPU count defines
            'spec_cpu_defines': {
                'pattern': r'#define\s+MAX_CPU\s+\d+',
                'replacement': '#define MAX_CPU 1',
                'description': 'Set MAX_CPU to 1'
            },

            # Remove SPEC memory size defines
            'spec_memory_defines': {
                'pattern': r'#define\s+(SMALL_MEMORY|BIG_MEMORY)\s*',
                'replacement': '',
                'description': 'Remove SPEC memory size defines'
            },

            # Remove SPEC performance measurement code
            'spec_performance_code': {
                'pattern': r'/\*\s*SPEC:\s*.*?\*/',
                'replacement': '',
                'description': 'Remove SPEC performance measurement comments'
            },

            # Fix SPEC-modified time measurement
            'spec_time_measurement': {
                'pattern': r'#if\s+defined\(SPEC\)\s*\n.*?return\s+0;\s*\n.*?#else\s*\n(.*?)\n#endif',
                'replacement': r'\1',
                'description': 'Use real time measurement instead of SPEC stub'
            },

            # Remove SPEC test environment setup
            'spec_test_env': {
                'pattern': r'/\*\s*SPEC\s+version:.*?\*/',
                'replacement': '',
                'description': 'Remove SPEC test environment comments'
            }
        }

        # Additional cleanups for restored functionality
        self.restorations = {
            # Restore typical chess engine features that SPEC might have disabled
            'enable_pondering': {
                'pattern': r'int allow_pondering\s*=\s*FALSE;',
                'replacement': 'int allow_pondering = TRUE;',
                'description': 'Ensure pondering is enabled'
            },

            'enable_logging': {
                'pattern': r'int cfg_logging\s*=\s*0;',
                'replacement': 'int cfg_logging = 1;',
                'description': 'Re-enable logging'
            },

            # Restore dynamic behavior
            'restore_randomization': {
                'pattern': r'\/\* SPEC: randomization disabled \*\/',
                'replacement': '',
                'description': 'Remove randomization disable comments'
            },

            # Restore normal chess engine main function
            'restore_main_function': {
                'pattern': r'mysrand\(12345\);',
                'replacement': 'mysrand((unsigned int)time(NULL));',
                'description': 'Use proper random seed instead of fixed SPEC seed'
            },

            # Restore normal time controls
            'restore_time_controls': {
                'pattern': r'gamestate\.time_left = 15 \* 60 \* 100;',
                'replacement': 'gamestate.time_left = 300 * 100; // 5 minutes default',
                'description': 'Set reasonable default time control'
            },

            # Remove SPEC fixed seed
            'remove_fixed_seed': {
                'pattern': r'mysrand\(12345\);',
                'replacement': 'mysrand((unsigned int)time(NULL));',
                'description': 'Use time-based random seed'
            },

            # Remove SPEC hardcoded seeds - more specific
            'remove_hardcoded_seeds_31657': {
                'pattern': r'mysrand\(31657\);',
                'replacement': 'mysrand((unsigned int)time(NULL));',
                'description': 'Use time-based random seed instead of hardcoded 31657'
            },

            'remove_hardcoded_seeds_12345': {
                'pattern': r'mysrand\(12345\);',
                'replacement': 'mysrand((unsigned int)time(NULL));',
                'description': 'Use time-based random seed instead of hardcoded 12345'
            },

            # Restore time functions
            'restore_time_functions': {
                'pattern': r'int rtime\( void \)\s*\{\s*\n\s*return 0;\s*\n\}',
                'replacement': '''int rtime(void) {
#ifdef WIN32
    return GetTickCount();
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 100 + tv.tv_usec / 10000;
#endif
}''',
                'description': 'Restore actual time function implementation'
            },

            # Restore rdifftime function
            'restore_rdifftime_function': {
                'pattern': r'int rdifftime\(int end, int start\) \{\s*\n\s*return 0;\s*\n\}',
                'replacement': 'int rdifftime(int end, int start) {\n    return end - start;\n}',
                'description': 'Restore actual time difference function'
            },

            # Restore interrupt function
            'restore_interrupt_function': {
                'pattern': r'int interrupt\(void\) \{\s*\n\s*return 0;\s*\n\}',
                'replacement': '''int interrupt(void) {
#ifdef WIN32
    return _kbhit();
#else
    fd_set readfds;
    struct timeval tv;
    FD_ZERO(&readfds);
    FD_SET(STDIN_FILENO, &readfds);
    tv.tv_sec = 0;
    tv.tv_usec = 0;
    return select(1, &readfds, NULL, NULL, &tv) > 0;
#endif
}''',
                'description': 'Restore actual interrupt detection'
            },

            # Add necessary includes
            'add_time_includes': {
                'pattern': r'#include "config\.h"\n#include "sjeng\.h"',
                'replacement': '''#include "config.h"
#include "sjeng.h"
#ifdef WIN32
#include <windows.h>
#include <conio.h>
#else
#include <sys/time.h>
#include <sys/select.h>
#include <unistd.h>
#endif
#include <time.h>''',
                'description': 'Add necessary time and system includes'
            },

            # Restore UCI interface
            'restore_uci_interface': {
                'pattern': r'/\* Normal UCI/XBoard interface would go here \*/',
                'replacement': '''/* UCI/XBoard interface */
    if (argc > 1 && strcmp(argv[1], "uci") == 0) {
        uci_mode = TRUE;
    }

    // Main game loop would go here
    // This would include UCI command parsing, game play, etc.
    myprintf("Sjeng chess engine ready\\n");''',
                'description': 'Add basic UCI interface structure'
            },

            # Enable pondering by default
            'enable_pondering_default': {
                'pattern': r'allow_pondering = TRUE;',
                'replacement': 'allow_pondering = TRUE;',
                'description': 'Ensure pondering is enabled by default'
            },

            # Restore normal hash table sizing
            'restore_hash_sizing': {
                'pattern': r'TTSize = 1;',
                'replacement': 'TTSize = 15000000; // 15MB default hash size',
                'description': 'Restore reasonable hash table size'
            },

            # Fix SPEC-disabled features
            'restore_book_usage': {
                'pattern': r'use_book = FALSE;',
                'replacement': 'use_book = TRUE;',
                'description': 'Re-enable opening book usage'
            },

            # Restore normal evaluation
            'restore_eval_features': {
                'pattern': r'/\* SPEC: evaluation simplified \*/',
                'replacement': '',
                'description': 'Remove evaluation simplification comments'
            },

            # Fix thread safety
            'restore_thread_safety': {
                'pattern': r'PawnTT\[0\]',
                'replacement': 'PawnTT[0]',
                'description': 'Ensure correct pawn table indexing'
            },

            # Restore search features
            'restore_search_features': {
                'pattern': r'/\* SPEC: search features disabled \*/',
                'replacement': '',
                'description': 'Remove search feature disable comments'
            }
        }

        # Additional fixes for broken function structures
        self.structure_fixes = {
            # Handle specific ttable.cpp SPEC patterns more carefully
            'fix_ttable_patterns': {
                'pattern': r'int p, q;\s*\n\s*\}\s*\n\s*s->hash = \(CONST64U\(0xDEADBEEF\) << 32\) \+ CONST64U\(0xDEADBEEF\);\s*\n\s*s->pawnhash = \(CONST64U\(0xC0FFEE00\) << 32\) \+ CONST64U\(0xC0FFEE00\);\s*\n\}',
                'replacement': '''void initialize_hash(state_t *s) {
    int p, q = 0;

    for (p = 0; p < 14; p++) {
        for (q = 0; q < 64; q++) {
            zobrist[p][q] = (((BITBOARD)myrandom()) << 32) + (BITBOARD)myrandom();
        }
    }

    s->hash = (CONST64U(0xDEADBEEF) << 32) + CONST64U(0xDEADBEEF);
    s->pawnhash = (CONST64U(0xC0FFEE00) << 32) + CONST64U(0xC0FFEE00);
}''',
                'description': 'Fix broken hash initialization function'
            }
        }

    def clean_file_content(self, content):
        """Clean SPEC-specific code from file content."""
        original_content = content
        changes_made = []

        # Handle the specific EPD workload message replacement carefully
        # This is done first to avoid regex corruption
        if 'myprintf("Workload not found' in content:
            content = content.replace('myprintf("Workload not found\\n");', 'myprintf("Test file not found\\n");')
            content = content.replace('myprintf("Workload not found\n");', 'myprintf("Test file not found\n");')
            changes_made.append('Fix workload message')

        # Special handling for ttable.cpp zobrist function
        if 'initialize_zobrist' in content and '#if defined(SPEC)' in content:
            # More conservative approach - just clean the SPEC blocks without breaking structure
            content = re.sub(
                r'#if defined\(SPEC\)\s*\n\s*BITBOARD temp;\s*\n#endif\s*\n',
                '\n',
                content,
                flags=re.MULTILINE
            )
            content = re.sub(
                r'#if defined\(SPEC\)\s*\n\s*temp = \(\(BITBOARD\)myrandom\(\)\) << 32;\s*\n\s*temp \+= \(BITBOARD\)myrandom\(\);\s*\n\s*zobrist\[p\]\[q\] = temp;\s*\n#else\s*\n\s*zobrist\[p\]\[q\] = \(\(\(BITBOARD\)myrandom\(\)\) << 32\) \+ \(BITBOARD\)myrandom\(\);\s*\n#endif',
                '            zobrist[p][q] = (((BITBOARD)myrandom()) << 32) + (BITBOARD)myrandom();',
                content,
                flags=re.MULTILINE
            )
            changes_made.append('Clean SPEC zobrist patterns')

        # Apply structure fixes for any broken functions (but only if needed)
        for pattern_name, pattern_info in self.structure_fixes.items():
            old_content = content
            content = re.sub(
                pattern_info['pattern'],
                pattern_info['replacement'],
                content,
                flags=re.MULTILINE | re.DOTALL
            )

            if content != old_content:
                changes_made.append(pattern_info['description'])

        # Apply main cleaning patterns (excluding problematic ones)
        for pattern_name, pattern_info in self.patterns.items():
            # Skip patterns that might interfere with function structures or cause variable corruption
            if pattern_name in ['epd_testsuite_function', 'spec_zobrist_temp_var', 'spec_zobrist_assignment']:
                continue

            old_content = content

            if pattern_name in ['spec_function_decl', 'spec_ifdef_block', 'spec_time_measurement']:
                # Multi-line patterns with groups
                content = re.sub(
                    pattern_info['pattern'],
                    pattern_info['replacement'],
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
            else:
                # Single-line or simple patterns
                content = re.sub(
                    pattern_info['pattern'],
                    pattern_info['replacement'],
                    content,
                    flags=re.MULTILINE
                )

            if content != old_content:
                changes_made.append(pattern_info['description'])

        # Apply threadid replacement very carefully - replace the entire assignment
        if 's->threadid' in content:
            old_content = content
            # Replace the entire assignment statements that set threadid to 0
            content = content.replace('s->threadid = 0;', '/* s->threadid = 0; // Removed for single-thread operation */')
            # Also handle any other threadid assignments
            content = re.sub(r's->threadid\s*=\s*[^;]+;', '/* threadid assignment removed */', content)
            if content != old_content:
                changes_made.append('Replace SPEC threadid assignments with comments')

        # Apply restorations and add necessary includes
        for pattern_name, pattern_info in self.restorations.items():
            old_content = content
            content = re.sub(
                pattern_info['pattern'],
                pattern_info['replacement'],
                content,
                flags=re.MULTILINE | re.DOTALL
            )

            if content != old_content:
                changes_made.append(pattern_info['description'])

        # Add time.h include if we're using time() function and it's not already included
        if 'time(NULL)' in content and '#include <time.h>' not in content and '#include "time.h"' not in content:
            # Find the last #include and add time.h after it
            include_pattern = r'(#include\s+[<"][^>"]+[>"])'
            includes = re.findall(include_pattern, content)
            if includes:
                last_include = includes[-1]
                content = content.replace(last_include, last_include + '\n#include <time.h>')
                changes_made.append('Add time.h include for time() function')

        # Additional cleanup: remove extra blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Fix spacing around restored const keywords
        content = re.sub(r'const\s+(\w)', r'const \1', content)

        return content, changes_made

    def should_process_file(self, filepath):
        """Check if file should be processed based on extension."""
        extensions = {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx'}
        return filepath.suffix.lower() in extensions

    def process_file(self, input_path, output_path):
        """Process a single file."""
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            cleaned_content, changes = self.clean_file_content(content)

            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)

            return changes

        except Exception as e:
            print(f"Error processing {input_path}: {e}")
            return []

    def process_directory(self, input_dir, output_dir):
        """Process all files in a directory recursively."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        total_files = 0
        processed_files = 0
        total_changes = []

        for file_path in input_path.rglob('*'):
            if file_path.is_file():
                total_files += 1

                if self.should_process_file(file_path):
                    # Calculate relative path and output location
                    relative_path = file_path.relative_to(input_path)
                    output_file = output_path / relative_path

                    print(f"Processing: {relative_path}")
                    changes = self.process_file(file_path, output_file)

                    if changes:
                        processed_files += 1
                        total_changes.extend(changes)
                        print(f"  Changes: {', '.join(changes)}")
                    else:
                        print(f"  No SPEC code found")
                else:
                    # Copy non-source files as-is (except Makefile since user has their own)
                    if file_path.name.lower() != 'makefile':
                        output_file = output_path / file_path.relative_to(input_path)
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, output_file)

        return total_files, processed_files, total_changes

def main():
    parser = argparse.ArgumentParser(
        description='Remove SPEC proprietary code from Sjeng chess engine source',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python spec_cleaner.py bitboard.c bitboard_clean.c

  # Process entire directory
  python spec_cleaner.py sjeng_spec/ sjeng_clean/

  # Process with verbose output
  python spec_cleaner.py -v sjeng_spec/ sjeng_clean/
        """
    )

    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')

    args = parser.parse_args()

    cleaner = SpecCodeCleaner()
    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        if input_path.is_file():
            # Process single file
            if args.dry_run:
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                _, changes = cleaner.clean_file_content(content)
                print(f"Would apply changes to {input_path}:")
                for change in changes:
                    print(f"  - {change}")
            else:
                changes = cleaner.process_file(input_path, output_path)
                if changes:
                    print(f"Successfully cleaned {input_path}")
                    if args.verbose:
                        for change in changes:
                            print(f"  - {change}")
                else:
                    print(f"No SPEC code found in {input_path}")

        elif input_path.is_dir():
            # Process directory
            if args.dry_run:
                print("DRY RUN - No files will be modified")
                # Implement dry run for directory
                for file_path in input_path.rglob('*'):
                    if file_path.is_file() and cleaner.should_process_file(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        _, changes = cleaner.clean_file_content(content)
                        if changes:
                            print(f"\nWould modify {file_path.relative_to(input_path)}:")
                            for change in changes:
                                print(f"  - {change}")
            else:
                total_files, processed_files, all_changes = cleaner.process_directory(
                    input_path, output_path
                )

                print(f"\nSummary:")
                print(f"  Total files: {total_files}")
                print(f"  Files with SPEC code: {processed_files}")
                print(f"  Total changes made: {len(all_changes)}")

                if args.verbose and all_changes:
                    print(f"\nAll changes applied:")
                    change_counts = {}
                    for change in all_changes:
                        change_counts[change] = change_counts.get(change, 0) + 1

                    for change, count in sorted(change_counts.items()):
                        print(f"  {change}: {count} times")
        else:
            print(f"Error: {input_path} is not a file or directory")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

    print("SPEC code cleaning completed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
