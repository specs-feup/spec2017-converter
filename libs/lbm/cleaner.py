#!/usr/bin/env python3
"""
SPEC Proprietary Code Remover for LBM (Lattice Boltzmann Method) Fluid Dynamics Simulation

This script removes SPEC-specific modifications from the LBM source code,
restoring it closer to the original open-source version.

Usage:
    python cleaner.py input_file.c output_file.c
    python cleaner.py input_directory/ output_directory/
"""

import re
import os
import sys
import argparse
from pathlib import Path
import shutil

class LBMSpecCodeCleaner:
    def __init__(self):
        pass

    def clean_main_h(self, content):
        """Clean main.h"""
        # Remove SPEC conditionals around timing includes
        content = content.replace('#if !defined(SPEC)\n#include <sys/times.h>\n#endif', '#include <sys/times.h>')

        # Remove SPEC conditionals around timing struct
        content = content.replace('#if !defined(SPEC)\ntypedef struct {\n\tdouble timeScale;\n\tclock_t tickStart, tickStop;\n\tstruct tms timeStart, timeStop;\n\n} MAIN_Time;\n#endif',
                                 'typedef struct {\n\tdouble timeScale;\n\tclock_t tickStart, tickStop;\n\tstruct tms timeStart, timeStop;\n} MAIN_Time;')

        # Remove SPEC conditionals around function declarations
        content = content.replace('#if !defined(SPEC)\nvoid MAIN_startClock( MAIN_Time* time );\nvoid MAIN_stopClock( MAIN_Time* time, const MAIN_Param* param );\n#endif',
                                 'void MAIN_startClock( MAIN_Time* time );\nvoid MAIN_stopClock( MAIN_Time* time, const MAIN_Param* param );')

        return content

    def clean_main_c(self, content):
        """Clean main.c"""
        # Fix includes
        content = content.replace('#if defined(SPEC)\n#   include <time.h>\n#else\n#   include <sys/times.h>\n#   include <unistd.h>\n#endif',
                                 '#include <sys/times.h>\n#include <unistd.h>')

        # Remove SPEC conditionals around timing variable
        content = content.replace('#if !defined(SPEC)\n\tMAIN_Time time;\n#endif', '\tMAIN_Time time;')

        # Remove SPEC conditionals around timing calls
        content = content.replace('#if !defined(SPEC)\n\tMAIN_startClock( &time );\n#endif', '\tMAIN_startClock( &time );')
        content = content.replace('#if !defined(SPEC)\n\tMAIN_stopClock( &time, &param );\n#endif', '\tMAIN_stopClock( &time, &param );')

        # Ensure timing functions are always included
        if 'void MAIN_stopClock( MAIN_Time* time, const MAIN_Param* param ) {' not in content:
            timing_code = '''

void MAIN_startClock( MAIN_Time* time ) {
\ttime->timeScale = 1.0 / sysconf( _SC_CLK_TCK );
\ttime->tickStart = times( &(time->timeStart) );
}


/*############################################################################*/

void MAIN_stopClock( MAIN_Time* time, const MAIN_Param* param ) {
\ttime->tickStop = times( &(time->timeStop) );

\tprintf( "MAIN_stopClock:\\n"
\t        "\\tusr: %7.2f sys: %7.2f tot: %7.2f wct: %7.2f MLUPS: %5.2f\\n\\n",
\t        (time->timeStop.tms_utime - time->timeStart.tms_utime) * time->timeScale,
\t        (time->timeStop.tms_stime - time->timeStart.tms_stime) * time->timeScale,
\t        (time->timeStop.tms_utime - time->timeStart.tms_utime +
\t         time->timeStop.tms_stime - time->timeStart.tms_stime) * time->timeScale,
\t        (time->tickStop           - time->tickStart          ) * time->timeScale,
\t        1.0e-6 * SIZE_X * SIZE_Y * SIZE_Z * param->nTimeSteps /
\t        (time->tickStop           - time->tickStart          ) / time->timeScale );
}'''
            content += timing_code

        return content

    def clean_lbm_c(self, content):
        """Clean lbm.c"""
        # Fix OpenMP conditionals
        content = content.replace('(defined(_OPENMP) || defined(SPEC_OPENMP)) && !defined(SPEC_SUPPRESS_OPENMP) && !defined(SPEC_AUTO_SUPPRESS_OPENMP)', 'defined(_OPENMP)')

        # Fix memory allocation message
        content = content.replace('#ifndef SPEC\n\tprintf( "LBM_allocateGrid: allocated %.1f MByte\\n",\n\t        size / (1024.0*1024.0) );\n#endif',
                                 '\tprintf( "LBM_allocateGrid: allocated %.1f MByte\\n",\n\t        size / (1024.0*1024.0) );')

        # Fix variable types in endianness handling
        content = content.replace('#if !defined(SPEC)\n\t\tint i;\n#else\n               size_t i;\n#endif', '\t\tint i;')
        content = content.replace('#if !defined(SPEC)\n\t\t\tint i;\n\t\t#else\n\t\t               size_t i;\n\t\t#endif', '\t\t\tint i;')

        # Fix precision handling in scanf
        content = content.replace('#if !defined(SPEC)\n\t\t\t\tif( sizeof( OUTPUT_PRECISION ) == sizeof( double )) {\n\t\t\t\t\tfscanf( file, "%lf %lf %lf\\n", &fileUx, &fileUy, &fileUz );\n\t\t\t\t}\n\t\t\t\telse {\n#endif\n\t\t\t\t\tfscanf( file, "%f %f %f\\n", &fileUx, &fileUy, &fileUz );\n#if !defined(SPEC)\n\t\t\t\t}\n#endif',
                                 '\t\t\t\tfscanf( file, "%f %f %f\\n", &fileUx, &fileUy, &fileUz );')

        # Fix any remaining %lf format specifiers that should be %f (since OUTPUT_PRECISION is float)
        content = content.replace('fscanf( file, "%lf %lf %lf\\n"', 'fscanf( file, "%f %f %f\\n"')
        content = content.replace('"%lf %lf %lf\\n"', '"%f %f %f\\n"')

        # Fix output with error checking
        content = content.replace('#ifdef SPEC\n\tprintf( "LBM_compareVelocityField: maxDiff = %e  \\n\\n",\n\t        sqrt( maxDiff2 )  );\n#else\n\tprintf( "LBM_compareVelocityField: maxDiff = %e  ==>  %s\\n\\n",\n\t        sqrt( maxDiff2 ),\n\t        sqrt( maxDiff2 ) > 1e-5 ? "##### ERROR #####" : "OK" );\n#endif',
                                 '\tprintf( "LBM_compareVelocityField: maxDiff = %e  ==>  %s\\n\\n",\n\t        sqrt( maxDiff2 ),\n\t        sqrt( maxDiff2 ) > 1e-5 ? "##### ERROR #####" : "OK" );')

        return content

    def clean_file_content(self, content, filename):
        """Clean SPEC-specific code from file content based on filename."""
        original_content = content
        changes_made = []

        file_basename = os.path.basename(filename) if filename else 'unknown'

        if file_basename == 'main.h':
            content = self.clean_main_h(content)
            if content != original_content:
                changes_made.append('Removed SPEC conditionals from main.h')
        elif file_basename == 'main.c':
            content = self.clean_main_c(content)
            if content != original_content:
                changes_made.append('Removed SPEC conditionals and restored timing functions')
        elif file_basename == 'lbm.c':
            content = self.clean_lbm_c(content)
            if content != original_content:
                changes_made.append('Removed SPEC conditionals and fixed format specifiers')

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

            cleaned_content, changes = self.clean_file_content(content, str(input_path))

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
                    # Copy non-source files as-is (but skip Makefile)
                    if file_path.name.lower() != 'makefile':
                        output_file = output_path / file_path.relative_to(input_path)
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, output_file)

        return total_files, processed_files, total_changes

def main():
    parser = argparse.ArgumentParser(
        description='Remove SPEC proprietary code from LBM fluid dynamics simulation source',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single file
  python cleaner.py main.c main_clean.c

  # Process entire directory
  python cleaner.py lbm_spec_source/ lbm_clean/

  # Process with verbose output
  python cleaner.py -v lbm_spec_source/ lbm_clean/
        """
    )

    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('output', help='Output file or directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be changed without modifying files')

    args = parser.parse_args()

    cleaner = LBMSpecCodeCleaner()
    input_path = Path(args.input)
    output_path = Path(args.output)

    try:
        if input_path.is_file():
            # Process single file
            if args.dry_run:
                with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                _, changes = cleaner.clean_file_content(content, str(input_path))
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
                        _, changes = cleaner.clean_file_content(content, str(file_path))
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

    print("LBM SPEC code cleaning completed successfully!")
    print("\nNOTE: The cleaned version should now be a standard LBM implementation")
    print("without SPEC-specific modifications. You can compile and run it as a")
    print("normal fluid dynamics simulation.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
