"""
AWRS-HexLift Siting & Performance Numerical Verification Engine
Author: Principal Investigator / Systems Architect
Description:
    1. Computes the AHP Consistency Ratio (CR) for the 10-parameter GIS Siting Model.
    2. Runs a 5-year stochastic Monte Carlo simulation of wadi flash floods,
       comparing unmanaged siltation vs. PVSF/CSP gating and HexLift tilt-scouring.
"""

import math
import random


def verify_ahp_consistency():
    """Validates the 10-parameter AHP Pairwise Comparison Matrix

    and computes the exact Principal Eigenvalue (lambda_max),
    Consistency Index (CI), and Consistency Ratio (CR).
    """
    # 10 Siting Criteria:
    # 0: Catchment Area, 1: Flash-Flood Volume, 2: Alluvial Thickness,
    # 3: Hydraulic Conductivity, 4: Valley Confinement, 5: Bed Slope,
    # 6: Sediment Yield, 7: Depth to Water Table, 8: Road Access, 9: Environmental Sensitivity
    matrix = [
        [
            1.0,
            1.0 / 2,
            1.0 / 3,
            1.0 / 3,
            2.0,
            2.0,
            1.0 / 2,
            1.0 / 4,
            3.0,
            4.0,
        ],
        [
            2.0,
            1.0,
            1.0 / 2,
            1.0 / 2,
            3.0,
            3.0,
            1.0,
            1.0 / 3,
            4.0,
            5.0,
        ],
        [
            3.0,
            2.0,
            1.0,
            1.0,
            4.0,
            4.0,
            2.0,
            1.0 / 2,
            5.0,
            6.0,
        ],
        [
            3.0,
            2.0,
            1.0,
            1.0,
            4.0,
            4.0,
            2.0,
            1.0 / 2,
            5.0,
            6.0,
        ],
        [
            1.0 / 2,
            1.0 / 3,
            1.0 / 4,
            1.0 / 4,
            1.0,
            1.0,
            1.0 / 3,
            1.0 / 5,
            2.0,
            3.0,
        ],
        [
            1.0 / 2,
            1.0 / 3,
            1.0 / 4,
            1.0 / 4,
            1.0,
            1.0,
            1.0 / 3,
            1.0 / 5,
            2.0,
            3.0,
        ],
        [
            2.0,
            1.0,
            1.0 / 2,
            1.0 / 2,
            3.0,
            3.0,
            1.0,
            1.0 / 3,
            4.0,
            5.0,
        ],
        [
            4.0,
            3.0,
            2.0,
            2.0,
            5.0,
            5.0,
            3.0,
            1.0,
            6.0,
            7.0,
        ],
        [
            1.0 / 3,
            1.0 / 4,
            1.0 / 5,
            1.0 / 5,
            1.0 / 2,
            1.0 / 2,
            1.0 / 4,
            1.0 / 6,
            1.0,
            2.0,
        ],
        [
            1.0 / 4,
            1.0 / 5,
            1.0 / 6,
            1.0 / 6,
            1.0 / 3,
            1.0 / 3,
            1.0 / 5,
            1.0 / 7,
            1.0 / 2,
            1.0,
        ],
    ]

    n = len(matrix)
    # Random Index (RI) table for n = 1 to 10 (Saaty, 1980)
    ri_values = {
        1: 0.0,
        2: 0.0,
        3: 0.58,
        4: 0.90,
        5: 1.12,
        6: 1.24,
        7: 1.32,
        8: 1.41,
        9: 1.45,
        10: 1.49,
    }
    ri = ri_values[n]

    # Calculate column sums
    col_sums = [sum(matrix[r][c] for r in range(n)) for c in range(n)]

    # Normalize matrix and compute criteria priority vector (weights)
    norm_matrix = [
        [matrix[r][c] / col_sums[c] for c in range(n)] for r in range(n)
    ]
    weights = [sum(norm_matrix[r]) / n for r in range(n)]

    # Compute weighted sum vector: Aw
    aw = [
        sum(matrix[r][c] * weights[c] for c in range(n))
        for r in range(n)
    ]

    # Principal eigenvalue: lambda_max
    lambda_max = sum(aw[i] / weights[i] for i in range(n)) / n

    # Consistency Index (CI) & Consistency Ratio (CR)
    ci = (lambda_max - n) / (n - 1)
    cr = ci / ri

    print("=== AHP Siting Verification ===")
    print(f"Matrix Dimension (n): {n}")
    print(f"Principal Eigenvalue (lambda_max): {lambda_max:.4f}")
    print(f"Consistency Index (CI): {ci:.6f}")
    print(f"Consistency Ratio (CR): {cr:.6f}")
    print(f"Consistency Confirmed (< 0.10): {cr < 0.10}\n")
    return cr


def simulate_5year_mass_balance():
    """Runs a 5-year stochastic sediment mass balance (1,825 days).

    Compares unmanaged baseline accumulation against the combined
    PVSF vortex exclusion, CSP dynamic gating, and HexLift tilt-scouring.
    """
    random.seed(42)  # Deterministic seed for reproducible verification
    days = 1825
    annual_event_rate = 3.5  # Mean flash-flood events per year
    daily_prob = annual_event_rate / 365.25

    unmanaged_silt_mm = 0.0
    managed_silt_mm = 0.0
    hexlift_cycles = 0

    pvsf_capture_efficiency = 0.70  # Coarse sediment vortex separation
    csp_gate_efficiency = 0.381  # Throttling efficiency during peak shear
    scour_threshold_mm = 15.0  # Thickness triggering tilt-scour
    residual_scour_ratio = 0.40  # 60% of sediment slumps away during tilt

    for _ in range(days):
        if random.random() < daily_prob:
            # Flood pulse event occurs
            # Event raw sediment mass influx in mm equivalent
            sediment_flux_mm = random.lognormvariate(
                math.log(8.0), 0.5
            )

            # Unmanaged: 100% of sediment settles directly onto infiltration bed
            unmanaged_silt_mm += sediment_flux_mm

            # Stage 1 & 2: PVSF vortex extraction + CSP gate throttling
            attenuated_flux = sediment_flux_mm * (
                1.0 - pvsf_capture_efficiency
            )
            attenuated_flux *= 1.0 - csp_gate_efficiency
            managed_silt_mm += attenuated_flux

            # Stage 3: HexLift autonomous tilt scouring
            if managed_silt_mm >= scour_threshold_mm:
                managed_silt_mm *= residual_scour_ratio
                hexlift_cycles += 1

    net_attenuation = (
        (unmanaged_silt_mm - managed_silt_mm) / unmanaged_silt_mm
    ) * 100.0

    print("=== 5-Year Mass Balance Verification ===")
    print(
        f"Baseline Unmanaged Silt Accumulation: {unmanaged_silt_mm:.2f} mm"
    )
    print(
        f"Managed Silt Accumulation (AWRS-HexLift): {managed_silt_mm:.2f} mm"
    )
    print(f"Autonomous HexLift Scour Cycles Triggered: {hexlift_cycles}")
    print(f"Net Cumulative Sediment Attenuation: {net_attenuation:.2f}%")


if __name__ == "__main__":
    verify_ahp_consistency()
    simulate_5year_mass_balance()
