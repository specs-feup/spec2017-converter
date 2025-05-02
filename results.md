# SPEC CPU2017 Benchmark Execution Summary

## Commands Used for Each Benchmark

The following command was used to run each benchmark:

```bash
runcpu --config=config --size=test --copies=1 --noreportable --iterations=1 all
```

## Expected Outcomes

- **Success**: The benchmark builds and runs successfully, producing valid results.
- **Error**: The benchmark fails to build or run, resulting in an error.

## Benchmark Results

### Integer Speed (intspeed)

- **Success**:
  - 600.perlbench_s
  - 602.gcc_s
  - 605.mcf_s
  - 620.omnetpp_s
  - 623.xalancbmk_s
  - 625.x264_s
  - 631.deepsjeng_s
  - 641.leela_s
  - 657.xz_s
  - 998.specrand_is

- **Error**:
  - 648.exchange2_s

### Integer Rate (intrate)

- **Success**:
  - 500.perlbench_r
  - 502.gcc_r
  - 505.mcf_r
  - 520.omnetpp_r
  - 523.xalancbmk_r
  - 525.x264_r
  - 531.deepsjeng_r
  - 541.leela_r
  - 557.xz_r
  - 999.specrand_ir

- **Error**:
  - 548.exchange2_r

### Floating Point Speed (fpspeed)

- **Build Errors**:
  - 603.bwaves_s
  - 607.cactuBSSN_s
  - 621.wrf_s
  - 627.cam4_s
  - 628.pop2_s
  - 649.fotonik3d_s
  - 654.roms_s

### Floating Point Rate (fprate)

- **Build Errors**:
  - 503.bwaves_r
  - 507.cactuBSSN_r
  - 508.namd_r
  - 510.parest_r
  - 511.povray_r
  - 519.lbm_r
  - 521.wrf_r
  - 526.blender_r
  - 527.cam4_r
  - 538.imagick_r
  - 544.nab_r
  - 549.fotonik3d_r
  - 554.roms_r
  - 997.specrand_fr

