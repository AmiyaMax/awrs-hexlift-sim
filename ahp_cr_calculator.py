"""
AHP Pairwise Comparison Weight + Consistency Ratio (CR) Calculator
====================================================================
Solo-usable: fill in YOUR OWN pairwise judgments in the matrix below
(no team or workshop needed) and run this script.

HOW TO FILL THE MATRIX
-----------------------
For each pair of criteria (i, j), enter how much more important i is
than j on Saaty's 1-9 scale:
  1 = equal importance          5 = strongly more important
  3 = moderately more important 7 = very strongly more important
                                 9 = extremely more important
  (2,4,6,8 = intermediate values)
If j is more important than i instead, enter the RECIPROCAL (e.g. 1/3).
The diagonal is always 1 (a criterion compared to itself).
The matrix must be reciprocal: matrix[j][i] = 1 / matrix[i][j].

Below is a placeholder matrix for the 10 criteria from Part 1 of the
draft, in this order:
  1. Wadi order/position       6. Catchment area/runoff
  2. Channel cross-section     7. Soil infiltration class
  3. Adjacent ridges/bedrock   8. Slope of wadi bed
  4. Alluvial fan proximity    9. Distance to settlements
  5. Flash-flood hazard       10. Land tenure/accessibility

REPLACE THE VALUES BELOW WITH YOUR OWN JUDGMENTS before trusting the
output -- this placeholder is only to demonstrate the calculation.
"""

import numpy as np

# Saaty's Random Index (RI) lookup table, indexed by matrix size n
RANDOM_INDEX = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59,
}

CRITERIA = [
    "Wadi order/position", "Channel cross-section", "Adjacent ridges/bedrock",
    "Alluvial fan proximity", "Flash-flood hazard", "Catchment area/runoff",
    "Soil infiltration class", "Slope of wadi bed", "Distance to settlements",
    "Land tenure/accessibility",
]

# ---- PLACEHOLDER MATRIX: replace with your own pairwise judgments ----
# This example roughly reproduces the indicative weights from the draft.
matrix = np.array([
    [1,    2,    1.5,  2,    1.5,  1.5,  2.5,  3,    4,    6   ],
    [0.50, 1,    0.8,  1.3,  0.9,  1,    1.7,  2,    3,    5   ],
    [0.67, 1.25, 1,    1.3,  0.9,  1.1,  1.8,  2.2,  3,    5   ],
    [0.50, 0.77, 0.77, 1,    0.7,  0.9,  1.3,  1.8,  2.5,  4   ],
    [0.67, 1.11, 1.11, 1.43, 1,    1.2,  2,    2.5,  3.5,  5.5 ],
    [0.67, 1,    0.91, 1.11, 0.83, 1,    1.6,  2,    2.7,  4.5 ],
    [0.40, 0.59, 0.56, 0.77, 0.50, 0.63, 1,    1.3,  1.8,  3   ],
    [0.33, 0.50, 0.45, 0.56, 0.40, 0.50, 0.77, 1,    1.4,  2.3 ],
    [0.25, 0.33, 0.33, 0.40, 0.29, 0.37, 0.56, 0.71, 1,    1.7 ],
    [0.17, 0.20, 0.20, 0.25, 0.18, 0.22, 0.33, 0.43, 0.59, 1   ],
])


def compute_ahp_weights_and_cr(matrix: np.ndarray, criteria_names):
    n = matrix.shape[0]
    assert matrix.shape[0] == matrix.shape[1], "Matrix must be square"
    assert len(criteria_names) == n, "Criteria list must match matrix size"

    # Priority vector via the normalized-column-average method
    # (simple, transparent, solo-computable without needing eigen-decomposition
    # by hand -- though we also compute lambda_max via eigenvalues below)
    col_sums = matrix.sum(axis=0)
    normalized = matrix / col_sums
    weights = normalized.mean(axis=1)

    # lambda_max via Ax = lambda*x, using the weight vector as x
    weighted_sum_vector = matrix @ weights
    lambda_max = np.mean(weighted_sum_vector / weights)

    ci = (lambda_max - n) / (n - 1)
    ri = RANDOM_INDEX.get(n)
    cr = ci / ri if ri else float("nan")

    return weights, lambda_max, ci, cr


if __name__ == "__main__":
    weights, lambda_max, ci, cr = compute_ahp_weights_and_cr(matrix, CRITERIA)

    print("=== AHP Weight & Consistency Ratio Calculator ===\n")
    print(f"{'Criterion':<30}{'Weight':>10}")
    for name, w in zip(CRITERIA, weights):
        print(f"{name:<30}{w:>10.4f}")

    print(f"\nSum of weights: {weights.sum():.4f}  (should be ~1.0 by construction)")
    print(f"Lambda max: {lambda_max:.4f}")
    print(f"Consistency Index (CI): {ci:.4f}")
    print(f"Consistency Ratio (CR): {cr:.4f}")

    if cr < 0.10:
        print("\nResult: CR < 0.10 -- judgments are acceptably consistent.")
    else:
        print("\nResult: CR >= 0.10 -- judgments are inconsistent; revisit "
              "the pairwise comparisons above (look for contradictions, e.g. "
              "A > B, B > C, but C > A) and re-run.")
