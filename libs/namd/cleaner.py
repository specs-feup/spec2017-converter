import os
import re
import shutil
import sys

def main(input_dir, output_dir):
    """
    Cleans and transforms source files from input_dir, outputs to output_dir:
    1. Replaces specific SSE2 macro block in ComputeNonbondedBase.h.
    2. Removes lines exactly '#ifndef SPEC' or '#endif // !SPEC'.
    3. Replaces '#if defined(WIN32) || defined(SPEC_NEED_ERFC)' with '#if defined(WIN32)'.
    4. Replaces '#ifdef SPEC_NEED_ERFC' with '#if 0  // originally: #ifdef SPEC_NEED_ERFC'.
    5. Renames 'spec_namd.C' to 'main.c'.
    6. Copies 'Makefile' (located alongside this script) into the output_dir.
    """

    # Copy the entire input directory to output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    shutil.copytree(input_dir, output_dir)
    print(f"Copied '{input_dir}' to '{output_dir}'")

    # Step 1: Replace SSE2 block in ComputeNonbondedBase.h
    sse2_pattern = re.compile(
        r"""(?mx)
        \#if\s+defined\(__SSE2__\)\s+&&\s+!\s+defined\(NAMD_DISABLE_SSE\)\n
        \#include\s+<emmintrin\.h>.*?\n
        \#if\s+defined\(__INTEL_COMPILER\)\n
        \#define\s+__align\(X\)\s+__declspec\(align\(X\)\s\)\n
        \#elif\s+defined\(__GNUC__\)\s+\|\|\s+defined\(__PGI\)\n
        \#define\s+__align\(X\)\s+__attribute__\(\(aligned\(X\)\s\)\)\n
        \#else\n
        \#define\s+__align\(X\)\s+__declspec\(align\(X\)\s\)\n
        \#endif\n
        \#endif
        """
    )

    sse2_replacement = """#if defined(__SSE2__) && ! defined(NAMD_DISABLE_SSE)
#include <emmintrin.h>  // We're using SSE2 intrinsics
#define __align(X)  __attribute__((aligned(X) ))
#endif"""

    cnb_path = os.path.join(output_dir, "ComputeNonbondedBase.h")
    if os.path.isfile(cnb_path):
        with open(cnb_path, "r") as f:
            content = f.read()
        content = sse2_pattern.sub(sse2_replacement, content)
        with open(cnb_path, "w") as f:
            f.write(content)
        print(f"Updated SSE2 block in '{cnb_path}'")

    # Step 2: Process all files
    for dirpath, _, filenames in os.walk(output_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()

                new_lines = []
                modified = False

                for line in lines:
                    stripped = line.strip()
                    if stripped in ("#ifndef SPEC", "#endif // !SPEC"):
                        modified = True
                        continue
                    elif stripped == "#if defined(WIN32) || defined(SPEC_NEED_ERFC)":
                        new_lines.append("#if defined(WIN32)\n")
                        modified = True
                    elif stripped == "#ifdef SPEC_NEED_ERFC":
                        new_lines.append("#if 0  // originally: #ifdef SPEC_NEED_ERFC\n")
                        modified = True
                    else:
                        new_lines.append(line)

                if modified:
                    with open(file_path, "w") as f:
                        f.writelines(new_lines)
                    print(f"Cleaned '{file_path}'")

            except Exception as e:
                print(f"Error processing '{file_path}': {e}")

    # Step 3: Rename spec_namd.C to main.C
    for dirpath, _, filenames in os.walk(output_dir):
        for filename in filenames:
            if filename == "spec_namd.C":
                old_path = os.path.join(dirpath, filename)
                new_path = os.path.join(dirpath, "main.C")

                os.rename(old_path, new_path)
                print(f"Renamed '{filename}' to 'main.C'")

                break

    script_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_copy = ["Makefile", "apoa1.input"]

    for filename in files_to_copy:
        src = os.path.join(script_dir, filename)
        dst = os.path.join(output_dir, filename)

        if os.path.isfile(src):
            shutil.copyfile(src, dst)
            print(f"Copied {filename} to '{output_dir}'")
        else:
            print(f"{filename} not found next to script. Skipped copying.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 cleaner.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        sys.exit(1)

    main(input_dir, output_dir)
