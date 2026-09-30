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
### Prerequisites
- Python 3.9+
- NumPy, Matplotlib

```bash
pip install numpy matplotlib
