"""NEXUS Hybrid Compute Fabric: scalable logical architecture simulator.

Logical lane counts are metadata for architecture exploration. This program
does not instantiate physical cores, allocate accelerator memory, or claim
measured FLOPS. It models topology and distributes a workload description
across heterogeneous engine classes.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import asdict, dataclass
from typing import Dict


@dataclass(frozen=True)
class Engine:
    name: str
    role: str
    logical_units: int
    lanes_per_unit: int
    supported_workloads: tuple[str, ...]
    execution_model: str

    @property
    def logical_lanes(self) -> int:
        return self.logical_units * self.lanes_per_unit


ENGINES = (
    Engine("N-SIMT", "programmable parallel graphics and general compute",
           1_000_000, 32, ("graphics", "parallel", "simulation"), "warp/wavefront"),
    Engine("N-TENSOR", "dense matrix and AI training operations",
           262_144, 256, ("matmul", "training", "transformer"), "systolic/tile"),
    Engine("N-INFER", "low-precision inference and vector operators",
           524_288, 128, ("inference", "embedding", "attention"), "vector/dataflow"),
    Engine("N-RAY", "ray traversal and intersection workloads",
           131_072, 64, ("raytracing", "geometry"), "spatial traversal"),
    Engine("N-CRYPTO", "hashing and security primitives",
           65_536, 32, ("security",), "specialized pipeline"),
)

FABRIC = {
    "name": "NEXUS-HCF",
    "revision": "0.1-logical-topology",
    "tiers": [
        "host control plane",
        "global work scheduler",
        "chiplet/accelerator clusters",
        "SIMT, tensor, inference, ray and crypto engines",
        "local SRAM/scratchpad and cache hierarchy",
        "memory controllers and external memory",
        "high-speed scale-up/scale-out interconnect",
    ],
    "memory_domains": [
        {"name": "register_file", "scope": "per execution unit", "physical": False},
        {"name": "local_scratchpad", "scope": "per cluster", "physical": False},
        {"name": "shared_cache", "scope": "per chiplet", "physical": False},
        {"name": "HBM_or_system_memory", "scope": "external memory interface", "physical": False},
    ],
    "coherence": "explicit ownership + DMA/event fences; no assumed global coherent memory",
    "safety": "logical topology only; no physical device or memory is created",
}


def topology() -> dict:
    return {
        **FABRIC,
        "engines": [
            {**asdict(e), "supported_workloads": list(e.supported_workloads),
             "logical_lanes": e.logical_lanes}
            for e in ENGINES
        ],
        "total_logical_lanes": sum(e.logical_lanes for e in ENGINES),
        "physical_cores_created": 0,
        "physical_memory_allocated_bytes": 0,
        "measured_throughput": False,
    }


def route_workload(workload: str, operations: int) -> dict:
    if operations <= 0:
        raise ValueError("operations must be positive")
    matches = [e for e in ENGINES if workload in e.supported_workloads]
    if not matches:
        raise ValueError(f"unsupported workload: {workload}")
    engine = matches[0]
    # This is a logical work partition, not a runtime execution or speed estimate.
    waves = (operations + engine.logical_lanes - 1) // engine.logical_lanes
    return {
        "workload": workload,
        "engine": engine.name,
        "logical_lanes_available": engine.logical_lanes,
        "operation_count": operations,
        "logical_waves": waves,
        "executed": False,
        "runtime_seconds": None,
        "throughput": None,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--topology", action="store_true")
    p.add_argument("--route", choices=sorted({w for e in ENGINES for w in e.supported_workloads}))
    p.add_argument("--operations", type=int, default=1_000_000_000)
    a = p.parse_args()
    if a.route:
        print(json.dumps(route_workload(a.route, a.operations), indent=2))
    else:
        print(json.dumps(topology(), indent=2))


if __name__ == "__main__":
    main()
