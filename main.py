#!/usr/bin/env python3
import os
import subprocess
import sys

import installation


def run_all_unspec(benchspec_dir, output_dir):
    cmd = [
        sys.executable,
        'run_unspec_with_copy.py',
        '--benchspec', benchspec_dir,
        '--output',   output_dir
    ]
    subprocess.check_call(cmd)


if __name__ == "__main__":
    iso_path   = "cpu2017-1_0_5.iso"
    output_dir = "cpu2017"
    spec_out   = "spec2017-unspec"
    benchspec  = os.path.join(output_dir, 'benchspec', 'CPU')

    # 1) Se ainda não extraiu o SPEC, faz a instalação
    if not os.path.isdir(benchspec):
        print("Extraindo SPEC CPU2017...")
        installation.main(iso_path, output_dir)

    # 2) Corre o script de unspec + check
    run_all_unspec(benchspec, spec_out)

    print(f"Processo concluído. Confira: {spec_out}/pass e {spec_out}/fail")
