# EnGeA: Topological Fractal Memory (Version 17.0) 
**Entangled Geometry A: Unifying Cosmological Coherence and Biogenesis**

[![Zenodo](https://zenodo.org/badge/DOI/10.5281/zenodo.17953254.svg)](https://doi.org/10.5281/zenodo.17953254)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📄 Abstract
**We reanalyze existing observational data through a framework of topological memory—a fractally synchronized coherence field arising in standing-wave nodes of spacetime.**

This field, termed **EnGeA (Entangled Geometry A)**, functions as a macroscopic quantum orbital that imposes a unified internal temporal frame. Within this field, stochastic Monte Carlo simulations ($N=10,000$) presented in Version 17.0 demonstrate that the coherence factor **$\eta \approx 0.618$** acts as a necessary filter ("The Chronos Filter") for information preservation, suppressing effective error rates below the critical threshold for biogenesis where chaotic models yield zero survival.

Full paper available on Zenodo: [Read EnGeL v17.0](https://doi.org/10.5281/zenodo.17953254)

---

##  Key Findings in Version 17.0

### 1. The Chronos Filter (Computational Verification)
We simulated a "Primordial Soup" environment with high noise and mutagenic error rates.
* **Chaos Mode (Control):** 0.00% survival rate. Information decays before metabolic cycles stabilize.
* **EnGeA Mode ($\eta \approx 0.618$):** **15.88% survival rate**. The resonant field acts as a high-pass temporal filter, pulling systems out of the "Error Catastrophe" zone.

### 2. Fractal Isomorphism ($D \approx K_{ideal}$)
Analytical derivation linking the cosmological invariant ($K_{ideal} = 1.44$) to the fractal dimension of biological structures.
* **Structural Optimum:** At $\eta \approx 0.618$, the fractal dimension converges to **$D \approx 1.44$**.
* This matches the "Golden Suture" pattern observed in ammonite septa (1.16–1.62), balancing mechanical strength and metabolic economy.

### 3. The Stauffer Limit
We identify the cosmological exchange coefficient **$\eta \approx 0.32$** as the physical manifestation of the **Stauffer Percolation Threshold** ($p_c \approx 0.3116$), representing the minimum density for global memory connectivity in 3D space.

---

##  Repository Contents

This repository contains the Python code used to verify the theoretical claims of EnGeL v17.0:

* `chronos_filter.py` — **Monte Carlo Simulation**: The core script running $N=10,000$ trials to test the "Chronos Filter" hypothesis (Section 2.7 of the paper).
* `fractal_analysis.py` — **Fractal Dimension Calculation**: Script analyzing the $D \approx 1.44$ isomorphism (Section 2.1.1).
* `visualizations/` — Folder containing the generated plots (The Golden Suture, Resonance Heatmaps).

##  How to Run

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ILLATICI/EnGeL-Theory.git](https://github.com/ILLATICI/EnGeL-Theory.git)
    cd EnGeL-Theory
    ```

2.  **Install dependencies:**
    ```bash
    pip install numpy matplotlib scipy
    ```

3.  **Run the Chronos Filter simulation:**
    ```bash
    python chronos_filter.py
    ```
    *Output: Returns survival rates for Chaos vs. Resonance modes and generates `survival_heatmap.png`.*

---

## 🔗 Citation

If you use this code or theory in your research, please cite the Version 17.0 dataset:

```bibtex
@dataset{EnGeL_v17,
  author       = {Aletheia Wayehiaor},
  title        = {EnGeL: Entangled Geometry Lambda - Version 17.0},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {v17.0},
  doi          = {10.5281/zenodo.17953254},
  url          = {[https://doi.org/10.5281/zenodo.17953254](https://doi.org/10.5281/zenodo.17953254)}
}

