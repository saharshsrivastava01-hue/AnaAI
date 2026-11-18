# NEXUS-HCF: Hybrid Compute Fabric

NEXUS-HCF is a proposed heterogeneous accelerator architecture inspired by
general-purpose GPU execution, tensor/systolic arrays, and inference-focused
accelerators. It is an independent architecture concept, not a copy of NVIDIA,
Google, or Meta silicon.

## Engine families

| Engine | Intended work | Execution model |
|---|---|---|
| N-SIMT | Graphics, programmable parallel kernels, simulation | 32-lane warp/wavefront abstraction |
| N-TENSOR | Matrix multiplication, transformer training | Tiled systolic/dataflow array |
| N-INFER | Low-precision inference, embeddings, attention | Vector/dataflow pipeline |
| N-RAY | BVH traversal, ray/triangle intersection | Spatial traversal pipeline |
| N-CRYPTO | Security primitives | Specialized pipeline |

The simulator currently describes 176,160,768 logical lanes across these engine
families. That is an architecture parameter—not a physical core count, not
active parallel hardware, and not a performance claim. The topology can be
scaled in configuration without allocating those resources.

## System hierarchy

1. Host control plane and runtime API.
2. Global scheduler with workload classification and admission control.
3. Accelerator clusters / chiplets.
4. Specialized execution engines.
5. Register files, local SRAM/scratchpad and cache hierarchy.
6. Memory controllers (HBM or system memory interface).
7. Scale-up and scale-out interconnect with DMA and event fences.

A real implementation needs a defined ISA, compiler, driver/runtime, physical
memory design, clock/power management, RTL for each engine, verification,
synthesis, place-and-route, and FPGA/ASIC validation. Merely increasing logical
lane counts does not increase physical compute.

## Run the topology simulator

```bash
python nexus_hybrid_fabric.py --topology
python nexus_hybrid_fabric.py --route matmul --operations 1000000000
python nexus_hybrid_fabric.py --route graphics --operations 50000000
```

The router reports logical waves only. It does not execute the workload.

## Roadmap

- P0: logical topology and workload classification (this prototype).
- P1: specify instruction formats, scheduling semantics, memory ordering and
  DMA protocol.
- P2: implement one small SIMT lane group and one tensor MAC tile in SystemVerilog.
- P3: simulation, assertions, randomized tests and formal checks.
- P4: synthesize to FPGA and measure real clock, area, bandwidth and throughput.
- P5: compiler/runtime and scaling across multiple FPGA boards or custom silicon.

## Honest comparison rule

Do not compare this simulator's logical lanes with NVIDIA CUDA cores, Google
TPU matrix units, or Meta accelerator silicon. Compare only measured workloads
on implemented hardware, with precision, memory size/bandwidth, power, software
stack and benchmark methodology disclosed.
