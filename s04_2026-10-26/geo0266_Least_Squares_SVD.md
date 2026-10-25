# geo0266 Least squares and the SVD: a line fit step by step (optional)

**Tool:** Jupyter notebook `geo0266_Least_Squares_SVD.ipynb` · **Time:** about 1.5 h for §1–§4, 1 h more for the stretch tasks §5–§7 · **Builds on:** geo0264 §1.2–§1.4 (*The maths*, the solver, PDOP) · **Data:** none

This is an **optional** task for everyone who wants to know what `np.linalg.lstsq` does inside the GNSS solver of geo0264. It is not graded and not needed for the next sessions.

The example is as small as possible: a straight line through five points. You compute the singular value decomposition (SVD) of its design matrix by hand, solve the least-squares problem with it, and then use the singular values to judge how well the unknowns are determined. At the end you apply the same idea to a GNSS design matrix and find the reason why GNSS heights are worse than horizontal positions.

## Tasks
1. **The problem (§1):** set up the design matrix, predict and compute $A^TA$, solve the normal equations.
2. **The idea (§2):** look at how $A$ turns the unit circle of parameters into an ellipse of measurements.
3. **The SVD by hand (§3):** eigenvalues of $A^TA$ → singular values; eigenvectors → $V$; $\mathbf{u}_i = A\mathbf{v}_i / s_i$ → $U$. Check against `np.linalg.svd`.
4. **Least squares with the SVD (§4):** $\mathbf{p} = V\Sigma^{-1}U^T\mathbf{y}$ in three steps; find where the residuals live.
5. **Stretch (§5–§6):** conditioning (points far from $x = 0$, centring), why `lstsq` beats the normal equations, rank deficiency.
6. **Stretch, back to GNSS (§7):** covariance and PDOP from the SVD; the weakest direction.
7. **Wrap-up (§8):** answer the questions.

## Hints
- Every exercise cell ends with a check (`assert`). If it fails, read the message before you change anything else.
- Predict before you run, especially in §5.
- Singular vectors are only defined up to sign. A column of yours with the opposite sign to NumPy's is fine as long as $\mathbf{u}_i$ and $\mathbf{v}_i$ flip together.
- `A @ V / s` divides each column by its own singular value (broadcasting).

## Hand in
Nothing. If you want feedback, upload the notebook (with outputs) to Moodle and say which result surprised you.

## Sources
- Wikipedia: *Singular value decomposition*, *Linear least squares*, *Moore–Penrose inverse*, *Condition number*, *Dilution of precision (navigation)*.
- G. H. Golub, C. F. Van Loan: *Matrix Computations*, 4th ed., 2013.
- G. Strang: *Introduction to Linear Algebra*, 5th ed., 2016.
