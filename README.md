# AWRS-HexLift: Numerical Modeling & Verification Engine

**Autonomous Wadi Recharge System (AWRS-HexLift)**  
*Managed Aquifer Recharge (MAR) with Passive Vortex Desilting, Dynamic Shear Intake Gating, and Buoyancy-Assisted Anti-Blinding Beds*

---

## Overview

This repository hosts the quantitative verification scripts, stochastic mass-balance simulations, and multi-criteria siting decision models supporting the AWRS-HexLift grant proposal (GPIW Award Submission - Environmental Sustainability).

AWRS-HexLift resolves the fundamental failure mode of Managed Aquifer Recharge (MAR) in hyper-arid ephemeral wadis: **rapid surface pore-blinding from high-turbidity flood fronts**.

### The Three-Stage Architecture
1. **Upstream Separation:** Passive Vortex Sediment Forebay (PVSF) with helical boundary-layer circulation to centrifugally eject coarse bedload (>70% exclusion).
2. **Intake Throttling:** Dynamic Critical Shear-Permeability (CSP) gating calibrated to the critical Shields threshold, admitting water while throttling hyper-turbid fine sediment pulses.
3. **Infiltration Bed Regeneration:** Tessellated hexagonal cassettes (HexLift) that tilt to 45° via buoyancy assistance to trigger Mohr-Coulomb limit-equilibrium liquefaction and flush settled silt cakes.

---

## Repository Contents

| File | Description |
| :--- | :--- |
| `ahp_cr_calculator.py` | Saaty Analytical Hierarchy Process (AHP) 10-parameter siting matrix and Consistency Ratio (CR) solver. |
| `awrs_hexlift_sim.py` | 5-year (1,825-day) stochastic discrete-time mass-balance simulation of wadi flood pulses and desiltation mechanics. |
| `awrs_hexlift_results.csv` | Daily time-series export of bed sediment depth (mm) and cumulative flush events. |
| `awrs_hexlift_simulation.png` | Verification plot comparing unmanaged baseline sedimentation vs. full AWRS-HexLift mitigation. |

---

## Quickstart & Reproducibility

### Prerequisites
- Python 3.9+
- NumPy, Matplotlib

```bash
pip install numpy matplotlib
