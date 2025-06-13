#!/usr/bin/env python3
"""
MCF SPEC Code Cleaner

This script removes SPEC-specific modifications from the MCF (Minimum Cost Flow)
optimizer source code, restoring it closer to the original open-source version.

Usage:
    python mcf_spec_cleaner.py input_file.c output_file.c
    python mcf_spec_cleaner.py input_directory/ output_directory/
"""

import re
import os
import sys
import argparse
from pathlib import Path
import shutil

class MCFSpecCodeCleaner:
    def __init__(self):
            # Patterns to identify and clean SPEC-specific code
            self.patterns = {
                # Remove SPEC conditional compilation includes
                'spec_qsort_include': {
                    'pattern': r'#if defined\(SPEC\)\s*\n#\s*include\s+"spec_qsort\.h"\s*\n#endif',
                    'replacement': '',
                    'description': 'Remove SPEC qsort include'
                },

                # Remove SPEC includes
                'spec_include_qsort': {
                    'pattern': r'#if defined\(SPEC\)\s*\n#\s*include\s+"spec_qsort\.h"\s*\n#endif\s*\n',
                    'replacement': '',
                    'description': 'Remove SPEC qsort header include'
                },

                # Remove SPEC stdint includes
                'spec_stdint_includes': {
                    'pattern': r'#ifdef SPEC\s*\n#\s*include <stdint\.h>\s*\n#\s*if defined\(SPEC_WINDOWS\) && !defined\(SPEC_HAVE_INTTYPES_H\)\s*\n#\s*include "win32/inttypes\.h"\s*\n#\s*else\s*\n#\s*include <inttypes\.h>\s*\n#\s*endif\s*\n/\* inttypes\.h is just to get PRId64; if it\'s not present \(not C99\?\), guess \*/\s*\n#\s*if !defined\(PRId64\)\s*\n#\s*if defined\(SPEC_LP64\) \|\| defined\(SPEC_ILP64\)\s*\n#\s*define PRId64 "ld"\s*\n#\s*else\s*\n#\s*define PRId64 "lld"\s*\n#\s*endif\s*\n#\s*endif\s*\n#\s*define LONG int64_t\s*\n#else\s*\n#\s*define LONG long\s*\n#endif',
                    'replacement': '#define LONG long\n#include <inttypes.h>\n#ifndef PRId64\n#define PRId64 "ld"\n#endif',
                    'description': 'Replace SPEC stdint includes with standard includes'
                },

                # Remove SPEC OpenMP conditionals
                'spec_openmp_conditionals': {
                    'pattern': r'#if \(defined\(_OPENMP\) \|\| defined\(SPEC_OPENMP\)\) && !defined\(SPEC_SUPPRESS_OPENMP\) && !defined\(SPEC_AUTO_SUPPRESS_OPENMP\)',
                    'replacement': '#ifdef _OPENMP',
                    'description': 'Simplify OpenMP conditionals'
                },

                # Remove SPEC qsort calls
                'spec_qsort_calls': {
                    'pattern': r'#if defined\(SPEC\)\s*\n\s*spec_qsort\((.*?)\);\s*\n#else\s*\n\s*qsort\((.*?)\);\s*\n#endif',
                    'replacement': r'        qsort(\2);',
                    'description': 'Use standard qsort instead of SPEC version'
                },

                # Remove SPEC comments and headers
                'spec_header_comments': {
                    'pattern': r', SPEC version',
                    'replacement': '',
                    'description': 'Remove SPEC version indicators from headers'
                },

                # Remove SPEC memory limits
                'spec_memory_limits': {
                    'pattern': r'#if defined\(SPEC\)\s*\n#define MAX_NEW_ARCS_SMALL_NET 2000000\s*\n#else\s*\n#define MAX_NEW_ARCS_SMALL_NET 5000000\s*\n#endif',
                    'replacement': '#define MAX_NEW_ARCS_SMALL_NET 5000000',
                    'description': 'Use non-SPEC memory limits'
                },

                # Remove SPEC Windows detection
                'spec_windows_detection': {
                    'pattern': r'defined\(SPEC_WINDOWS\)',
                    'replacement': 'defined(_WIN32)',
                    'description': 'Use standard Windows detection'
                },

                # Remove SPEC timing conditionals
                'spec_timing_conditionals': {
                    'pattern': r'#ifndef SPEC\s*\n(.*?time.*?)\n#endif',
                    'replacement': r'\1',
                    'description': 'Enable timing code'
                },

                # Remove SPEC thread number output suppression
                'spec_thread_output': {
                    'pattern': r'#ifndef SPEC\s*\n#ifdef _OPENMP\s*\n\s*printf\(\s*"number of threads\s*:\s*%d\\n",\s*omp_get_max_threads\(\)\s*\);\s*\n#else\s*\n\s*printf\(\s*"single threaded\\n"\s*\);\s*\n#endif\s*\n#endif',
                    'replacement': '#ifdef _OPENMP\n  printf( "number of threads          : %d\\n", omp_get_max_threads() );\n#else\n  printf( "single threaded\\n" );\n#endif',
                    'description': 'Enable thread count output'
                },

                # Remove SPEC report conditionals
                'spec_report_conditionals': {
                    'pattern': r'#if defined\(REPORT\) \|\| defined\(SPEC\)',
                    'replacement': '#ifdef REPORT',
                    'description': 'Simplify report conditionals'
                },

                # Remove SPEC defines and ifdefs
                'spec_defines': {
                    'pattern': r'#ifdef SPEC\s*\n.*?\n#endif\s*\n',
                    'replacement': '',
                    'description': 'Remove SPEC-only code blocks'
                },

                # Remove standalone SPEC conditionals
                'spec_standalone_blocks': {
                    'pattern': r'#if defined\(SPEC\)\s*\n(.*?)\n#endif',
                    'replacement': '',
                    'description': 'Remove SPEC-only conditional blocks'
                },

                # Remove SPEC version strings in main output
                'spec_version_output': {
                    'pattern': r'printf\(\s*"\\nMCF SPEC CPU version',
                    'replacement': 'printf( "\\nMCF version',
                    'description': 'Remove SPEC from version string'
                },

                # Fix PRId64 format specifiers in printf statements
                'fix_printf_format': {
                    'pattern': r'printf\(\s*"([^"]*?)%"\s*PRId64\s*"([^"]*?)",',
                    'replacement': r'printf( "\1%ld\2",',
                    'description': 'Replace PRId64 with %ld in printf statements'
                },

                # Fix multiline printf statements with PRId64
                'fix_multiline_printf': {
                    'pattern': r'printf\(\s*"([^"]*?)%"\s*PRId64\s*"([^"]*?)"',
                    'replacement': r'printf( "\1%ld\2"',
                    'description': 'Fix multiline printf format strings'
                },

                # Clean up AT_ZERO undef for SPEC
                'spec_at_zero_undef': {
                    'pattern': r'/\* #define AT_ZERO\s+3\s+NOT ALLOWED FOR THE SPEC VERSION \*/\s*\n#undef AT_ZERO',
                    'replacement': '#define AT_ZERO 3',
                    'description': 'Re-enable AT_ZERO for non-SPEC version'
                },

                # Remove SPEC debug suppressions
                'spec_debug_defines': {
                    'pattern': r'//#define DEBUG 1\s*\n//#define AT_HOME 1',
                    'replacement': '#define DEBUG 1\n#define AT_HOME 1',
                    'description': 'Enable debug and AT_HOME defines'
                },

                # Remove SPEC from prototype detection in prototyp.h
                'spec_prototype_macro': {
                    'pattern': r'defined\(__STDC__\)\s*\|\|\s*defined\(__cplusplus\)\s*\|\|\s*defined\(WANT_STDC_PROTO\)\s*\|\|\s*defined\(SPEC\)',
                    'replacement': 'defined(__STDC__) || defined(__cplusplus) || defined(WANT_STDC_PROTO)',
                    'description': 'Remove SPEC from prototype detection'
                },

                # Remove SPEC-style numbered output pattern
                'spec_numbered_output': {
                    'pattern': r'if \(argc == 3\) \{\s*\n\s*outnum = atoi\(argv\[2\]\);\s*\n\s*sprintf\(outfile,"mcf\.%d\.out",outnum\);\s*\n\s*\} else \{\s*\n\s*strcpy\(outfile,"mcf\.out"\);\s*\n\s*\}',
                    'replacement': 'strcpy(outfile, "mcf.out");',
                    'description': 'Simplify output file handling (remove SPEC numbered outputs)'
                },

                # Remove SPEC-style checksum output
                'spec_checksum_output': {
                    'pattern': r'printf\(\s*"checksum\s*:\s*%0\.0f\\n",\s*net\.optcost\s*\);',
                    'replacement': 'printf( "optimal cost               : %.0f\\n", net.optcost );',
                    'description': 'Replace checksum output with more descriptive text'
                },

                # Remove SPEC hardcoded constants
                'spec_hardcoded_limits': {
                    'pattern': r'#define MAX_NB_TRIPS_FOR_SMALL_NET 15000\s*\n#define MAX_NEW_ARCS_SMALL_NET 5000000\s*\n#define MAX_NEW_ARCS_LARGE_NET 28900000',
                    'replacement': '#define MAX_NB_TRIPS_FOR_SMALL_NET 15000\n#define MAX_NEW_ARCS_SMALL_NET 8000000\n#define MAX_NEW_ARCS_LARGE_NET 40000000',
                    'description': 'Increase limits beyond SPEC constraints'
                },

                # Remove SPEC memory buffer constants
                'spec_memory_buffers': {
                    'pattern': r'#define MAX_NEW_ARCS_PUFFER_LARGE_NET 4000000\s*\n#define MAX_NEW_ARCS_PUFFER_SMALL_NET 1000000',
                    'replacement': '#define MAX_NEW_ARCS_PUFFER_LARGE_NET 8000000\n#define MAX_NEW_ARCS_PUFFER_SMALL_NET 2000000',
                    'description': 'Increase memory buffers beyond SPEC limits'
                },

                # Remove SPEC iteration limits
                'spec_iteration_limits': {
                    'pattern': r'#define ITERATIONS_FOR_SMALL_NET\s+1000\s*\n#define ITERATIONS_FOR_BIG_NET\s+2000',
                    'replacement': '#define ITERATIONS_FOR_SMALL_NET  2000\n#define ITERATIONS_FOR_BIG_NET    5000',
                    'description': 'Increase iteration limits for better optimization'
                },

                # Fix SPEC-style minimal input validation
                'spec_minimal_validation': {
                    'pattern': r'if\(\s*argc\s*<\s*2\s*\)\s*\n\s*return\s*-1;',
                    'replacement': 'if( argc < 2 ) {\n    printf("Usage: %s input_file [output_number]\\n", argv[0]);\n    printf("  input_file: MCF problem input file\\n");\n    printf("  output_number: optional output file number (creates mcf.N.out)\\n");\n    return -1;\n  }',
                    'description': 'Add proper usage information'
                },

                # Enable timing that SPEC might suppress
                'spec_timing_suppression': {
                    'pattern': r'#ifndef SPEC\s*\n(.*?time.*?)\s*\n#endif',
                    'replacement': r'\1',
                    'description': 'Re-enable timing code suppressed for SPEC'
                },

                # Remove SPEC version indicator from output
                'spec_version_string': {
                    'pattern': r'printf\(\s*"MCF version 1\.11\\n"\s*\);',
                    'replacement': 'printf( "MCF version 1.11 (open source)\\n" );',
                    'description': 'Clarify this is the open source version'
                },

                # Fix SPEC-style thread reporting suppression
                'spec_thread_reporting': {
                    'pattern': r'//\s*printf\(\s*"number of threads\s*:\s*%d\\n",\s*omp_get_max_threads\(\)\s*\);',
                    'replacement': 'printf( "number of threads          : %d\\n", omp_get_max_threads() );',
                    'description': 'Re-enable thread count reporting'
                },

                # Remove SPEC force single-threading
                'spec_force_single_thread': {
                    'pattern': r'//\s*omp_set_num_threads\(1\);\s*//\s*Uncomment to force single thread',
                    'replacement': '// omp_set_num_threads(1); // Uncomment to force single thread',
                    'description': 'Clean up threading comments'
                },

                # Handle SPEC scanf patterns specifically - exact format from readmin.c
                'spec_scanf_2param': {
                    'pattern': r'#ifdef SPEC\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%"\s*PRId64\s*"\s*%"\s*PRId64\s*,\s*&t,\s*&h\s*\)\s*!=\s*2\s*\)\s*\n#else\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%ld\s*%ld",\s*&t,\s*&h\s*\)\s*!=\s*2\s*\)\s*\n#endif',
                    'replacement': '    if( sscanf( instring, "%ld %ld", &t, &h ) != 2 )',
                    'description': 'Fix 2-parameter scanf format'
                },

                'spec_scanf_2param_variant': {
                    'pattern': r'#ifdef SPEC\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%"\s*PRId64\s*"\s*%"\s*PRId64\s*,\s*&t,\s*&h\s*\)\s*!=\s*2\s*\|\|\s*t\s*>\s*h\s*\)\s*\n#else\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%ld\s*%ld",\s*&t,\s*&h\s*\)\s*!=\s*2\s*\|\|\s*t\s*>\s*h\s*\)\s*\n#endif',
                    'replacement': '        if( sscanf( instring, "%ld %ld", &t, &h ) != 2 || t > h )',
                    'description': 'Fix 2-parameter scanf format with condition'
                },

                'spec_scanf_3param': {
                    'pattern': r'#ifdef SPEC\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%"\s*PRId64\s*"\s*%"\s*PRId64\s*"\s*%"\s*PRId64\s*,\s*&t,\s*&h,\s*&c\s*\)\s*!=\s*3\s*\)\s*\n#else\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%ld\s*%ld\s*%ld",\s*&t,\s*&h,\s*&c\s*\)\s*!=\s*3\s*\)\s*\n#endif',
                    'replacement': '        if( sscanf( instring, "%ld %ld %ld", &t, &h, &c ) != 3 )',
                    'description': 'Fix 3-parameter scanf format'
                },

                # Remove SPEC prototype detection
                'spec_prototype_detection': {
                    'pattern': r'defined\(__STDC__\)\s*\|\|\s*defined\(__cplusplus\)\s*\|\|\s*defined\(WANT_STDC_PROTO\)\s*\|\|\s*defined\(SPEC\)',
                    'replacement': 'defined(__STDC__) || defined(__cplusplus) || defined(WANT_STDC_PROTO)',
                    'description': 'Remove SPEC from prototype detection'
                },

                # Handle SPEC inttypes include guard
                'spec_inttypes_guard': {
                    'pattern': r'#if !defined\(SPEC\)\s*\n#include "stdint\.h"\s*\n#endif',
                    'replacement': '#include <stdint.h>',
                    'description': 'Use standard stdint.h include'
                },

                # Prevent DEBUG from being undefined
                'spec_debug_undef': {
                    'pattern': r'#undef DEBUG\s*\n',
                    'replacement': '// #undef DEBUG  // Keep DEBUG enabled\n',
                    'description': 'Keep DEBUG enabled'
                },

                # Enhanced prototyp.h specific patterns
                'prototyp_spec_removal': {
                    'pattern': r'(defined\(__STDC__\)\s*\|\|\s*defined\(__cplusplus\)\s*\|\|\s*defined\(WANT_STDC_PROTO\))\s*\|\|\s*defined\(SPEC\)',
                    'replacement': r'\1',
                    'description': 'Remove SPEC from prototype detection macro in prototyp.h'
                },

                'prototyp_spec_standalone': {
                    'pattern': r'\|\|\s*defined\(SPEC\)',
                    'replacement': '',
                    'description': 'Remove standalone SPEC condition from prototyp.h'
                },

                'prototyp_clean_whitespace': {
                    'pattern': r'(#define _PROTO_\( args \)\s+args)\s*\n\s*\n\s*\n',
                    'replacement': r'\1\n\n',
                    'description': 'Clean up extra whitespace in prototyp.h after SPEC removal'
                },

                'prototyp_fix_conditional': {
                    'pattern': r'#if\s+defined\(__STDC__\)\s*\|\|\s*defined\(__cplusplus\)\s*\|\|\s*defined\(WANT_STDC_PROTO\)\s*\n',
                    'replacement': '#if defined(__STDC__) || defined(__cplusplus) || defined(WANT_STDC_PROTO)\n',
                    'description': 'Normalize conditional formatting in prototyp.h'
                },

                # Special handling for prototyp.h file structure
                'prototyp_header_guard': {
                    'pattern': r'(#ifndef _PROTOTYP_H\s*\n#define _PROTOTYP_H\s*\n\s*)(.*?)(#endif\s*\n?)$',
                    'replacement': r'\1\2\3',
                    'description': 'Preserve prototyp.h header guard structure'
                }
            }

            # Restorations for MCF-specific functionality
            self.restorations = {
                # Restore includes that might be needed
                'add_standard_includes': {
                    'pattern': r'(#include <stdio\.h>)',
                    'replacement': r'\1\n#include <time.h>\n#include <sys/time.h>',
                    'description': 'Add standard timing includes'
                },

                # Ensure proper LONG definition
                'ensure_long_definition': {
                    'pattern': r'#define LONG long\s*\n#include <inttypes\.h>',
                    'replacement': '#include <inttypes.h>\n#include <stdint.h>\n#define LONG long',
                    'description': 'Ensure proper LONG type definition'
                },

                # Restore normal qsort usage
                'restore_qsort_usage': {
                    'pattern': r'spec_qsort\(',
                    'replacement': 'qsort(',
                    'description': 'Use standard qsort function'
                },

                # Enable timing by default
                'enable_timing': {
                    'pattern': r'#ifdef INTERNAL_TIMING',
                    'replacement': '#define INTERNAL_TIMING\n#ifdef INTERNAL_TIMING',
                    'description': 'Enable internal timing'
                },

                # Remove //omp_set_num_threads(1); comment for SPEC
                'enable_omp_threads': {
                    'pattern': r'//omp_set_num_threads\(1\);',
                    'replacement': '// omp_set_num_threads(1); // Uncomment to force single thread',
                    'description': 'Allow multi-threading by default'
                },

                # Fix printf format for checksum
                'fix_checksum_format': {
                    'pattern': r'printf\("ORG_COST: %f",',
                    'replacement': 'printf("ORG_COST: %.0f\\n",',
                    'description': 'Fix format for ORG_COST output'
                },

                # Clean up SPEC_OPENMP references
                'fix_spec_openmp_refs': {
                    'pattern': r'defined\(SPEC_OPENMP\)',
                    'replacement': 'defined(_OPENMP)',
                    'description': 'Replace SPEC_OPENMP with standard _OPENMP'
                },

                # Clean up SPEC_SUPPRESS_OPENMP references
                'fix_spec_suppress_openmp': {
                    'pattern': r'&& !defined\(SPEC_SUPPRESS_OPENMP\) && !defined\(SPEC_AUTO_SUPPRESS_OPENMP\)',
                    'replacement': '',
                    'description': 'Remove SPEC OpenMP suppression checks'
                },

                # Restore proper BIGM definition
                'restore_bigm_definition': {
                    'pattern': r'#define BIGM 1\.0e7',
                    'replacement': '#define BIGM 1.0e8  // Larger BigM for better numerical stability',
                    'description': 'Use larger BigM value for non-SPEC version'
                },

                # Enable full feature set
                'enable_full_features': {
                    'pattern': r'#undef AT_ZERO\s*',
                    'replacement': '#define AT_ZERO 3  // Enable AT_ZERO status for better optimization',
                    'description': 'Re-enable AT_ZERO status'
                },

                # Restore comprehensive error handling
                'restore_error_handling': {
                    'pattern': r'printf\(\s*"read error, exit\\n"\s*\);',
                    'replacement': 'printf( "Error reading input file: %s\\n", net.inputfile );\n    printf( "Please check file format and permissions.\\n" );',
                    'description': 'Add more descriptive error messages'
                },

                # Enable memory debugging reporting
                'enable_memory_reporting': {
                    'pattern': r'#if defined AT_HOME\s*\n(\s*printf.*?MB.*?\n)+#endif',
                    'replacement': '#ifdef DEBUG\n\\1#endif',
                    'description': 'Enable memory reporting in debug mode'
                },

                # Restore comprehensive output options
                'restore_output_options': {
                    'pattern': r'fprintf\(\s*out,\s*"%.0f\\n",\s*flow_cost\(net\)\s*\);',
                    'replacement': 'fprintf( out, "MCF Optimal Solution\\n" );\n  fprintf( out, "Objective value: %.0f\\n", flow_cost(net) );\n  fprintf( out, "Problem size: %ld nodes, %ld arcs\\n", net->n_trips, net->m );',
                    'description': 'Add comprehensive output format'
                }
            }

            # Structure fixes for broken patterns
            self.structure_fixes = {
                # Fix broken conditional compilation
                'fix_broken_conditionals': {
                    'pattern': r'#if defined\(SPEC\)\s*\n\s*\n#else\s*\n(.*?)\n#endif',
                    'replacement': r'\1',
                    'description': 'Fix broken SPEC conditionals'
                },

                # Fix pragma omp sections that might be malformed
                'fix_openmp_pragmas': {
                    'pattern': r'#pragma omp parallel for private\((.*?)\)\s*\n#endif\s*\nfor',
                    'replacement': '#pragma omp parallel for private(\\1)\nfor',
                    'description': 'Fix malformed OpenMP pragmas'
                },

                # Fix variable redefinition in implicit.c
                'fix_arc_redefinition': {
                    'pattern': r'(\s+register arc_t \*arcout, \*arcin, \*arcnew, \*stop, \*sorted_array, \*arc;.*?)(\s+arc_t\* arc = net->arcs;)',
                    'replacement': r'\1\n       arc = net->arcs;',
                    'description': 'Fix arc variable redefinition in implicit.c'
                }
            }

    def clean_prototyp_h_specific(self, content):
        """Special handling for prototyp.h file structure and SPEC removal."""
        if 'prototyp.h' not in str(getattr(self, 'current_file', '')):
            return content

        # Specific prototyp.h cleaning
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Handle the specific SPEC macro removal
            if 'defined(SPEC)' in line and '_PROTO_' in line:
                # Remove the || defined(SPEC) part
                line = re.sub(r'\s*\|\|\s*defined\(SPEC\)', '', line)
                # Clean up any remaining formatting issues
                line = re.sub(r'\s+\\\s*$', ' \\', line)

            # Clean up the conditional compilation line
            if line.strip().startswith('#if') and 'defined(__STDC__)' in line:
                line = re.sub(
                    r'defined\(__STDC__\)\s*\|\|\s*defined\(__cplusplus\)\s*\|\|\s*defined\(WANT_STDC_PROTO\)\s*\|\|\s*defined\(SPEC\)',
                    'defined(__STDC__) || defined(__cplusplus) || defined(WANT_STDC_PROTO)',
                    line
                )

            cleaned_lines.append(line)

        # Join back and clean up any extra whitespace
        content = '\n'.join(cleaned_lines)

        # Remove any orphaned SPEC references
        content = re.sub(r'\|\|\s*defined\(SPEC\)', '', content)

        # Ensure proper formatting of the _PROTO_ macro definition
        content = re.sub(
            r'(#if\s+defined\(__STDC__\)\s*\|\|\s*defined\(__cplusplus\)\s*\|\|\s*defined\(WANT_STDC_PROTO\)\s*\n)(#define _PROTO_\(\s*args\s*\)\s*args\s*\n)(#else\s*\n)(#define _PROTO_\(\s*args\s*\)\s*\n)(#endif)',
            r'\1\2\3\4\5',
            content,
            flags=re.MULTILINE
        )

        return content

    def validate_prototyp_h_cleaning(self, content):
        """Validate that prototyp.h has been properly cleaned of SPEC references."""
        issues = []

        if 'defined(SPEC)' in content:
            issues.append('SPEC macro still present in conditional compilation')

        if '|| defined(SPEC)' in content:
            issues.append('SPEC condition still present in macro definition')

        # Check for proper _PROTO_ macro structure
        if '_PROTO_' in content:
            # Should have both the args and empty versions
            if '#define _PROTO_( args ) args' not in content:
                issues.append('Missing standard _PROTO_ macro definition')

            if '#define _PROTO_( args )' not in content or content.count('#define _PROTO_') < 2:
                issues.append('Missing empty _PROTO_ macro definition')

        return issues

    def clean_file_content(self, content):
        """Clean SPEC-specific code from file content."""
        original_content = content
        changes_made = []

        # Apply structure fixes first
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

        # Special handling for prototyp.h
        if hasattr(self, 'current_file') and 'prototyp.h' in str(self.current_file):
            old_content = content
            content = self.clean_prototyp_h_specific(content)
            if content != old_content:
                changes_made.append('Applied prototyp.h specific SPEC cleanup')

        # Apply main cleaning patterns
        for pattern_name, pattern_info in self.patterns.items():
            old_content = content

            # Handle multi-line patterns
            if pattern_name in ['spec_stdint_includes', 'spec_qsort_calls', 'spec_timing_conditionals', 'spec_thread_output']:
                content = re.sub(
                    pattern_info['pattern'],
                    pattern_info['replacement'],
                    content,
                    flags=re.MULTILINE | re.DOTALL
                )
            else:
                content = re.sub(
                    pattern_info['pattern'],
                    pattern_info['replacement'],
                    content,
                    flags=re.MULTILINE
                )

            if content != old_content:
                changes_made.append(pattern_info['description'])

        # Apply restorations
        for pattern_name, pattern_info in self.restorations.items():
            old_content = content
            content = re.sub(
                pattern_info['pattern'],
                pattern_info['replacement'],
                content,
                flags=re.MULTILINE
            )
            if content != old_content:
                changes_made.append(pattern_info['description'])

        # Additional cleanup passes

        # Handle SPEC scanf patterns specifically
        content = re.sub(
            r'#ifdef SPEC\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%" PRId64 " %" PRId64\s*,\s*&t,\s*&h\s*\)\s*!=\s*2\s*\)\s*\n#else\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%ld %ld",\s*&t,\s*&h\s*\)\s*!=\s*2\s*\)\s*\n#endif',
            r'    if( sscanf( instring, "%ld %ld", &t, &h ) != 2 )',
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        content = re.sub(
            r'#ifdef SPEC\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%" PRId64 " %" PRId64\s*,\s*&t,\s*&h\s*\)\s*!=\s*2\s*\|\|\s*t\s*>\s*h\s*\)\s*\n#else\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%ld %ld",\s*&t,\s*&h\s*\)\s*!=\s*2\s*\|\|\s*t\s*>\s*h\s*\)\s*\n#endif',
            r'        if( sscanf( instring, "%ld %ld", &t, &h ) != 2 || t > h )',
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        content = re.sub(
            r'#ifdef SPEC\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%" PRId64 " %" PRId64 " %" PRId64\s*,\s*&t,\s*&h,\s*&c\s*\)\s*!=\s*3\s*\)\s*\n#else\s*\n\s*if\(\s*sscanf\(\s*instring,\s*"%ld %ld %ld",\s*&t,\s*&h,\s*&c\s*\)\s*!=\s*3\s*\)\s*\n#endif',
            r'        if( sscanf( instring, "%ld %ld %ld", &t, &h, &c ) != 3 )',
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Remove any remaining SPEC references in comments
        content = re.sub(r'/\*.*?SPEC.*?\*/', '', content, flags=re.DOTALL)

        # Remove SPEC from copyright lines
        content = re.sub(r'SPEC version\s*\n', '\n', content)

        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Remove any remaining SPEC conditional compilation directives
        content = re.sub(r'#if.*?defined\(SPEC\).*?\n', '', content)
        content = re.sub(r'#ifdef\s+SPEC.*?\n', '', content)
        content = re.sub(r'#ifndef\s+SPEC.*?\n', '', content)

        # Remove spec_qsort function calls
        content = re.sub(r'spec_qsort\(', 'qsort(', content)

        # Clean up OpenMP conditionals more thoroughly
        content = re.sub(
            r'#if \(defined\(_OPENMP\) \|\| defined\(SPEC_OPENMP\)\) && !defined\(SPEC_SUPPRESS_OPENMP\) && !defined\(SPEC_AUTO_SUPPRESS_OPENMP\)',
            '#ifdef _OPENMP',
            content
        )

        # Fix PRId64 format specifiers that might remain
        content = re.sub(r'%" PRId64 "', '%ld', content)
        content = re.sub(r'%"\s*PRId64\s*"', '%ld', content)

        # Fix broken printf statements from string replacement
        content = re.sub(r'printf\(\s*"\s*\n', 'printf( "\\n', content)
        content = re.sub(r'printf\(\s*"([^"]*?)"\s*\n\s*"([^"]*?)"', r'printf( "\1\2"', content)

        # Fix any broken multiline strings
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for broken printf statements
            if 'printf(' in line and line.count('"') % 2 == 1:
                # This line has an unclosed quote, look for the closing line
                j = i + 1
                while j < len(lines) and lines[j].strip() != '' and not lines[j].strip().endswith('");'):
                    line += lines[j].strip()
                    j += 1
                if j < len(lines):
                    line += lines[j].strip()
                    i = j
            fixed_lines.append(line)
            i += 1

        content = '\n'.join(fixed_lines)

        # Fix any remaining broken conditionals from SPEC removal
        lines = content.split('\n')
        cleaned_lines = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            # Skip empty conditionals that might be left after SPEC removal
            if line == '#else' and i + 1 < len(lines) and lines[i + 1].strip() == '#endif':
                i += 2  # Skip both #else and #endif
                continue
            cleaned_lines.append(lines[i])
            i += 1

        content = '\n'.join(cleaned_lines)

        # Fix any broken #endif statements left over
        lines = content.split('\n')
        cleaned_lines = []
        endif_balance = 0

        for line in lines:
            if line.strip().startswith('#if') or line.strip().startswith('#ifdef') or line.strip().startswith('#ifndef'):
                endif_balance += 1
                cleaned_lines.append(line)
            elif line.strip() == '#endif':
                if endif_balance > 0:
                    endif_balance -= 1
                    cleaned_lines.append(line)
                # Skip orphaned #endif statements
            elif line.strip().startswith('#else') or line.strip().startswith('#elif'):
                if endif_balance > 0:
                    cleaned_lines.append(line)
                # Skip orphaned #else/#elif statements
            else:
                cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)

        # Special handling for mcf.c main function issues
        if 'mcf.c' in str(self.current_file):
            # Fix the broken version string from SPEC removal
            content = re.sub(
                r'printf\(\s*"\s*\nMCF version',
                'printf( "\\nMCF version',
                content
            )

            # Ensure complete printf statements
            content = re.sub(
                r'printf\(\s*"([^"]*?)"\s*\n([^"]*?)"([^"]*?)"',
                r'printf( "\1\2\3"',
                content,
                flags=re.MULTILINE
            )

            # Fix any remaining broken strings
            content = re.sub(
                r'printf\(\s*"\s*\n\s*MCF version',
                'printf( "\\nMCF version',
                content
            )

        # Final pass: ensure we have proper includes
        if 'mcf.c' in str(self.current_file) or 'main' in content:
            if '#include <time.h>' not in content:
                content = content.replace('#include "mcf.h"', '#include "mcf.h"\n#include <time.h>')
                changes_made.append('Add time.h include to main file')

        # Ensure we don't include SPEC files that won't exist
        content = re.sub(r'#include\s*"spec_qsort\.h"', '', content)

        # Clean up header comments with SPEC version
        content = re.sub(r'/\*+\s*\n.*?SPEC version\s*\n', '/*\n', content, flags=re.MULTILINE)

        # Final comprehensive fixes for mcf.c
        if 'mcf.c' in str(self.current_file):
            # Fix all remaining PRId64 references
            content = re.sub(r'%" PRId64 "', '"%ld"', content)
            content = re.sub(r'PRId64', 'ld', content)

            # Fix the specific broken printf from version string replacement
            content = re.sub(
                r'printf\(\s*"\s*\nMCF version 1\.11\\n"\s*\);',
                'printf( "\\nMCF version 1.11\\n" );',
                content
            )

            # Fix concatenated printf statements that got merged incorrectly
            content = re.sub(
                r'printf\(\s*"([^"]*?)"\s*\);printf\(',
                r'printf( "\1" );\n  printf(',
                content
            )

            # Fix the specific copyright line with broken escaping
            content = re.sub(
                r'"([^"]*?)"\\"([^"]*?)"',
                r'"\1\2"',
                content
            )

            # Fix any instances where statements got merged without proper line breaks
            content = re.sub(
                r';\s*([a-zA-Z_][a-zA-Z0-9_]*\s*\()',
                r';\n  \1',
                content
            )

            # Specifically fix the "GbR (LBW)" string issue
            content = re.sub(
                r'Weider "\\"GbR \(LBW\)\\n"',
                r'Weider GbR (LBW)\\n"',
                content
            )

            # Fix multiline printf statements that got broken
            content = re.sub(
                r'printf\(\s*"([^"]*?)\s*\n\s*([A-Za-z][^"]*?)"\s*\);',
                r'printf( "\1\2" );',
                content,
                flags=re.MULTILINE | re.DOTALL
            )

            # Ensure proper string termination and spacing
            content = re.sub(
                r'printf\(\s*"\s*\n([^"]*?)\\n"\s*\);',
                r'printf( "\\n\1\\n" );',
                content
            )

            # Fix the specific copyright string issue
            content = re.sub(
                r'"GbR \(LBW\)\\n"\s*\);',
                r'"GbR (LBW)\\n" );',
                content
            )

        # Additional fix for implicit.c variable conflicts
        if 'implicit.c' in str(self.current_file):
            # Fix the specific arc variable redefinition issue
            # The problem is 'arc' is declared as register variable and then redeclared later
            content = re.sub(
                r'(\s+)arc_t\* arc = net->arcs;',
                r'\1arc = net->arcs;',
                content
            )

            # Also fix any other similar redefinitions
            content = re.sub(
                r'(\s+)arc_t \*arc = ',
                r'\1arc = ',
                content
            )

        # Remove any remaining SPEC-only file references
        if any(name in str(self.current_file) for name in ['spec_qsort.c', 'spec_qsort.h', 'inttypes.h']):
            # Skip processing SPEC-only files entirely
            return None, ['SPEC-only file skipped']

        return content, changes_made

    def should_process_file(self, filepath):
        """Check if file should be processed based on extension."""
        extensions = {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx'}
        return filepath.suffix.lower() in extensions

    def process_file(self, input_path, output_path):
        """Process a single file."""
        self.current_file = input_path  # Store for context-specific fixes

        # Skip SPEC-only files entirely
        if input_path.name in ['spec_qsort.c', 'spec_qsort.h', 'inttypes.h']:
            print(f"Skipping SPEC-only file: {input_path.name}")
            return ['SPEC-only file skipped']

        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            cleaned_content, changes = self.clean_file_content(content)

            # If clean_file_content returns None, skip this file
            if cleaned_content is None:
                return changes

            # Special validation for prototyp.h
            if input_path.name == 'prototyp.h' and cleaned_content:
                validation_issues = self.validate_prototyp_h_cleaning(cleaned_content)
                if validation_issues:
                    print(f"Warning: prototyp.h validation issues: {', '.join(validation_issues)}")
                    changes.extend([f"Validation issue: {issue}" for issue in validation_issues])

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
                    # Copy non-source files as-is (excluding SPEC-specific files)
                    if file_path.name.lower() not in ['makefile', 'spec_qsort.c', 'spec_qsort.h', 'inttypes.h']:
                        output_file = output_path / file_path.relative_to(input_path)
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, output_file)

        return total_files, processed_files, total_changes

def main():
    parser = argparse.ArgumentParser(
        description='Remove SPEC proprietary code from MCF optimizer source',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python mcf_spec_cleaner.py mcf.c mcf_clean.c

  # Process entire directory
  python mcf_spec_cleaner.py mcf_spec/ mcf_clean/

  # Process with verbose output
  python mcf_spec_cleaner.py -v mcf_spec/ mcf_clean/
        """
    )

    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')

    args = parser.parse_args()

    cleaner = MCFSpecCodeCleaner()
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

    print("MCF SPEC code cleaning completed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
