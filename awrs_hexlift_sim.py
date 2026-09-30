"""
AWRS-HexLift Multi-Stage Sediment Mass-Balance Simulation
============================================================

PURPOSE
-------
This is a discrete-time (daily), stochastic MASS-BALANCE simulation — not a
computational fluid dynamics (CFD) or hydraulic model. It demonstrates the
LOGIC and RELATIVE BENEFIT of the three-mechanism sediment management system
proposed for the Adaptive self-regulating Wadi Recharge System (AWRS):

  1. PVSF  (Passive Vortex Sediment Forebay)
     - Removes a fraction of coarse sediment from inflow BEFORE it reaches
       the bed, passively (no moving parts).

  2. HexLift (alternating tilt-hinge hexagonal cassette floor)
     - Alternating "active" modules tilt 30-60 deg around a captive hinge to
       open a sediment-release aperture once local accumulation crosses a
       threshold. A small number of flush gates beneath the sediment-
       collection zone (not one per module) carry the released sediment out.
       "Passive" modules stay fixed and simply provide structural floor area.

  3. CSP-K-Gate control (adaptive permeability-based intake control)
     - Between maintenance events, intake admission is modulated based on
       an effective permeability/infiltration proxy (K), rather than a
       fixed on/off gate, reducing sediment loading during high-turbidity
       events.

ALL PARAMETERS BELOW ARE ILLUSTRATIVE PLACEHOLDERS pending real pilot-site
data (rainfall, USLE sediment yield, catchment area). Replace the constants
in the CONFIG block with site-specific values once available (Part 7 of the
draft lists free data sources for this: CHIRPS/IMERG rainfall, USLE inputs
from DEM+soil+land-cover layers).

OUTPUT
------
- A CSV of daily state (bed sediment depth, cumulative flush events, etc.)
- A comparison plot: "No PVSF/No HexLift" (baseline, passive accumulation
  only) vs "Full AWRS-HexLift system" (PVSF + tilt-triggered HexLift +
  CSP-K-Gate throttling).
"""

import numpy as np
import csv

# ----------------------------------------------------------------------
# CONFIG — illustrative placeholders; replace with site-calibrated values
# ----------------------------------------------------------------------
SIM_DAYS = 365 * 5          # 5-year simulation horizon
RNG_SEED = 42

# Storm/sediment-influx model (stand-in for a USLE-derived event sediment
# yield time series once real rainfall + catchment data are available)
WET_SEASON_DAYS = set()     # populated below (e.g. days 150-240 each year = monsoon-like window)
STORM_PROB_WET = 0.18       # daily probability of a sediment-generating storm event, wet season
STORM_PROB_DRY = 0.02       # daily probability, dry season
SEDIMENT_MEAN_KG = 900.0    # mean sediment mass delivered per storm event (kg), lognormal
SEDIMENT_SIGMA = 0.6        # lognormal shape parameter (event-to-event variability)

# PVSF (Passive Vortex Sediment Forebay)
PVSF_COARSE_REMOVAL_EFF = 0.70   # fraction of incoming sediment removed before reaching bed

# CSP-K-Gate control: throttles intake admission fraction based on a simple
# turbidity/permeability proxy — larger storms get throttled harder as a
# stand-in for "reduce fine-sediment admission during high-turbidity events"
def csp_k_gate_admission_fraction(event_mass_kg):
    """Returns fraction of sediment mass admitted past the intake gate.
    Larger events -> more throttling (illustrative logistic-style curve)."""
    # Full admission for small events, tapering down for very large events
    return float(np.clip(1.2 - event_mass_kg / 1500.0, 0.35, 1.0))

# HexLift cassette floor
BED_AREA_M2 = 400.0              # illustrative dam-bed footprint
BULK_DENSITY_KG_M3 = 1400.0      # deposited sediment bulk density (loose, wet)
N_MODULES = 24                   # total hexagonal cassettes tiling the bed
ACTIVE_FRACTION = 0.5            # alternating pattern -> half the modules are "active" (tiltable)
TILT_TRIGGER_DEPTH_MM = 15.0     # local depth threshold (mm) that triggers a tilt/flush cycle
TILT_REMOVAL_EFFICIENCY = 0.85   # fraction of local accumulated sediment removed per flush event

# ----------------------------------------------------------------------
# Derive wet-season day-of-year set (illustrative: two 3-month windows/yr
# is NOT assumed; using one ~3-month wet window per year as placeholder)
# ----------------------------------------------------------------------
for year in range(6):
    base = year * 365
    WET_SEASON_DAYS.update(range(base + 150, base + 240))

rng = np.random.default_rng(RNG_SEED)


def simulate(use_pvsf: bool, use_hexlift: bool, use_csp_k_gate: bool):
    """Run the daily mass-balance simulation.

    Returns dict of daily arrays: bed_depth_mm, cum_flush_events
    """
    bed_mass_kg = 0.0                       # sediment currently resting on the bed
    module_local_mass_kg = np.zeros(N_MODULES)  # naive equal-split local accumulation per module
    n_active = int(round(N_MODULES * ACTIVE_FRACTION))
    active_idx = np.arange(0, N_MODULES, 2)[:n_active]  # alternating pattern

    bed_depth_mm_series = np.zeros(SIM_DAYS)
    cum_flush_events = np.zeros(SIM_DAYS, dtype=int)
    flush_count = 0

    module_area_m2 = BED_AREA_M2 / N_MODULES

    for day in range(SIM_DAYS):
        p = STORM_PROB_WET if day in WET_SEASON_DAYS else STORM_PROB_DRY
        event_mass_kg = 0.0
        if rng.random() < p:
            event_mass_kg = float(rng.lognormal(
                mean=np.log(SEDIMENT_MEAN_KG), sigma=SEDIMENT_SIGMA))

        # Stage 1: CSP-K-Gate intake throttling
        admitted_mass_kg = event_mass_kg
        if use_csp_k_gate and event_mass_kg > 0:
            admitted_mass_kg = event_mass_kg * csp_k_gate_admission_fraction(event_mass_kg)

        # Stage 2: PVSF passive coarse-sediment removal
        reaching_bed_kg = admitted_mass_kg
        if use_pvsf and admitted_mass_kg > 0:
            reaching_bed_kg = admitted_mass_kg * (1.0 - PVSF_COARSE_REMOVAL_EFF)

        # Deposit evenly across modules (simplification; real system would
        # have spatially heterogeneous deposition near the inlet)
        if reaching_bed_kg > 0:
            module_local_mass_kg += reaching_bed_kg / N_MODULES
            bed_mass_kg += reaching_bed_kg

        # Stage 3: HexLift tilt-triggered flushing (active modules only)
        if use_hexlift:
            for idx in active_idx:
                local_depth_mm = (module_local_mass_kg[idx] / BULK_DENSITY_KG_M3
                                   / module_area_m2) * 1000.0
                if local_depth_mm >= TILT_TRIGGER_DEPTH_MM:
                    removed_kg = module_local_mass_kg[idx] * TILT_REMOVAL_EFFICIENCY
                    module_local_mass_kg[idx] -= removed_kg
                    bed_mass_kg -= removed_kg
                    flush_count += 1

        bed_depth_mm_series[day] = (bed_mass_kg / BULK_DENSITY_KG_M3 / BED_AREA_M2) * 1000.0
        cum_flush_events[day] = flush_count

    return {
        "bed_depth_mm": bed_depth_mm_series,
        "cum_flush_events": cum_flush_events,
    }


if __name__ == "__main__":
    baseline = simulate(use_pvsf=False, use_hexlift=False, use_csp_k_gate=False)
    pvsf_only = simulate(use_pvsf=True, use_hexlift=False, use_csp_k_gate=True)
    full_system = simulate(use_pvsf=True, use_hexlift=True, use_csp_k_gate=True)

    # --- Write CSV of daily results ---
    with open("awrs_hexlift_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["day", "baseline_bed_depth_mm",
                          "pvsf_csp_only_bed_depth_mm",
                          "full_system_bed_depth_mm", "full_system_cum_flushes"])
        for d in range(SIM_DAYS):
            writer.writerow([
                d,
                round(baseline["bed_depth_mm"][d], 3),
                round(pvsf_only["bed_depth_mm"][d], 3),
                round(full_system["bed_depth_mm"][d], 3),
                int(full_system["cum_flush_events"][d]),
            ])

    # --- Summary printout ---
    print("=== AWRS-HexLift Multi-Stage Simulation Summary (illustrative) ===")
    print(f"Simulation horizon: {SIM_DAYS} days (~{SIM_DAYS/365:.1f} years)")
    print(f"Baseline (no PVSF, no HexLift, no CSP-K-Gate) final bed depth: "
          f"{baseline['bed_depth_mm'][-1]:.1f} mm")
    print(f"PVSF + CSP-K-Gate only (no HexLift) final bed depth: "
          f"{pvsf_only['bed_depth_mm'][-1]:.1f} mm")
    print(f"Full system (PVSF + CSP-K-Gate + HexLift) final bed depth: "
          f"{full_system['bed_depth_mm'][-1]:.1f} mm")
    print(f"Full system total tilt/flush events over horizon: "
          f"{full_system['cum_flush_events'][-1]}")

    upstream_reduction_pct = (1 - pvsf_only['bed_depth_mm'][-1] / baseline['bed_depth_mm'][-1]) * 100
    hexlift_marginal_pct = (1 - full_system['bed_depth_mm'][-1] / pvsf_only['bed_depth_mm'][-1]) * 100
    total_reduction_pct = (1 - full_system['bed_depth_mm'][-1] / baseline['bed_depth_mm'][-1]) * 100
    print(f"\nPVSF + CSP-K-Gate contribution (upstream, vs baseline): {upstream_reduction_pct:.1f}%")
    print(f"HexLift marginal contribution (on top of PVSF+CSP-K-Gate): {hexlift_marginal_pct:.1f}%")
    print(f"Total residual bed sediment reduction (full system vs baseline): {total_reduction_pct:.1f}%")

    # --- Plot ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    days = np.arange(SIM_DAYS)
    years = days / 365.0

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

    ax1.plot(years, baseline["bed_depth_mm"], label="Baseline (no mechanisms)",
              color="#b04a3f")
    ax1.plot(years, pvsf_only["bed_depth_mm"], label="PVSF + CSP-K-Gate only (no HexLift)",
              color="#d9a441")
    ax1.plot(years, full_system["bed_depth_mm"], label="Full system (+ HexLift)",
              color="#2f7a4f")
    ax1.set_ylabel("Bed sediment depth (mm)")
    ax1.set_title("Illustrative sediment accumulation: isolating each mechanism's contribution")
    ax1.legend()
    ax1.grid(alpha=0.3)

    ax2.plot(years, full_system["cum_flush_events"], color="#2f7a4f",
              label="Cumulative HexLift tilt/flush events")
    ax2.set_xlabel("Years")
    ax2.set_ylabel("Cumulative flush events")
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig("awrs_hexlift_simulation.png", dpi=150)
    print("\nSaved: awrs_hexlift_results.csv, awrs_hexlift_simulation.png")
