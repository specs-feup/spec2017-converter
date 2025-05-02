#!/usr/bin/env python3
import os
import subprocess
import sys
import argparse
import threading
import time
import installation


"""

def loading_animation(message="Processing... this may take a few minutes"):
    def animate():
        for _ in range(30):  # total duration: 30 * 0.2 = 6 seconds
            for dot_count in range(4):
                print(f"\r{message}{'.' * dot_count}   ", end='', flush=True)
                time.sleep(0.2)
        print("\r" + " " * (len(message) + 5), end="\r")  # clear the line

    t = threading.Thread(target=animate)
    t.start()
    return t

"""

def run_all_unspec(benchspec_dir, output_dir, verbose=False):
    cmd = [
        sys.executable,
        'run_unspec_with_copy.py',
        '--benchspec', benchspec_dir,
        '--output',   output_dir
    ]
    if verbose:
        cmd.append('--verbose')
    subprocess.check_call(cmd)



def main():
    parser = argparse.ArgumentParser(description="Run unspec process on SPEC benchmarks.")
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    iso_path   = "cpu2017-1_0_5.iso"
    output_dir = "cpu2017"
    spec_out   = "spec2017-unspec"
    benchspec  = os.path.join(output_dir, 'benchspec', 'CPU')

    # 1) Se ainda não extraiu o SPEC, faz a instalação
    if not os.path.isdir(benchspec):
        if args.verbose:
            print("Extraindo SPEC CPU2017...")
        installation.main(iso_path, output_dir)

    # 2) Corre o script de unspec + check
    run_all_unspec(benchspec, spec_out, args.verbose)

    """
    if not args.verbose:
        t = loading_animation()
    if not args.verbose:
        t.join()
   
    """
    print(f"Processo concluído. Confira: {spec_out}/pass e {spec_out}/fail")

if __name__ == "__main__":
    main()