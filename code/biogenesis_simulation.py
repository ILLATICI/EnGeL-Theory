# -*- coding: utf-8 -*-
"""
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
from typing import List, Dict, Optional
import os
import time

# ---
rng = np.random.default_rng(42)
OUTPUT_DIR = "engel_comprehensive_lab"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#
ENERGY_COHERENCE_FACTOR = 0.6
NOISE_DESTRUCT_FACTOR = 0.5
FIELD_PROTECTION_FACTOR = 0.95

@dataclass
class Params:
    #
    base_error: float
    res_width: float
    power: float

    #
    n_species: int = 20
    density: float = 0.6
    energy_grad: float = 1.0
    noise_level: float = 0.35
    membrane_threshold: float = 0.70
    membrane_leak: float = 0.15
    code_length: int = 64
    crit_error: float = 0.05
    ext_periods: List[float] = None
    f_eta: float = 0.61803 # Golden Ratio

    def __post_init__(self):
        if self.ext_periods is None:
            self.ext_periods = [1.0, 29.5, 3102.5]

# ---
def run_single_trial(p: Params, trial_id: int) -> Dict:
    # 1. Environment
    adj = rng.random((p.n_species, p.n_species))
    mask = rng.random((p.n_species, p.n_species)) < p.density
    adj *= mask
    np.fill_diagonal(adj, 0.0)
    row_sum = adj.sum(axis=1, keepdims=True) + 1e-12
    adj /= row_sum

    energy = p.energy_grad * rng.normal(1.0, 0.1)
    noise = p.noise_level * rng.normal(1.0, 0.15)

    # 2. Membrane Physics
    mem_stab = p.membrane_threshold + 0.3*energy - 0.4*noise
    cond_mem = mem_stab > 0.60

    # 3. Cycle Coherence
    eig = np.max(np.abs(np.linalg.eigvals(adj))).real
    # Normalized entropy
    prob = np.abs(adj)
    prob /= (prob.sum() + 1e-12)
    entropy = -np.sum(prob * np.log(prob + 1e-12)) / np.log(p.n_species)

    coh = eig*(1 + 0.6*energy) - (p.membrane_leak + 0.5*noise)
    loop = np.mean(np.diag(np.linalg.matrix_power(adj, 3)))
    cycle_score = coh + 0.15*entropy + 0.6*loop
    cond_cycle = cycle_score > 1.0

    # 4. EnGeL Field (Resonance)
    T_base = min(p.ext_periods) * (p.f_eta ** 2)
    T_int = T_base * rng.normal(1.0, 0.02)

    best_reson = 0.0
    for T in p.ext_periods:
        r = T / T_int
        diff = abs(r - round(r))
        score = np.exp(-(diff**2)/(2 * p.res_width**2))
        if score > best_reson: best_reson = score

    prot = FIELD_PROTECTION_FACTOR * (best_reson ** p.power)
    eff_error = p.base_error * (1.0 - prot) * (1.0 + 0.1*(p.code_length/64))
    cond_gene = eff_error < p.crit_error

    # 5. Result & Fail Reason
    success = False
    fail_reason = "None"

    if cond_mem and cond_cycle and cond_gene:
        success = True
    else:
        # Hierarchical failure (Biological priority)
        if not cond_mem: fail_reason = "Membrane"
        elif not cond_cycle: fail_reason = "Cycle"
        elif not cond_gene: fail_reason = "Genetic"

    # Invariant I
    I_val = abs(coh) / (T_int + 1e-9)

    return {
        "base_error": p.base_error,
        "width": p.res_width,
        "power": p.power,
        "trial": trial_id,
        "reson_factor": best_reson,
        "eff_error": eff_error,
        "mem_stab": mem_stab,
        "cycle_score": cycle_score,
        "T_int": T_int,
        "I": I_val,
        "success": int(success),
        "fail_reason": fail_reason
    }

# ---

def run_experiment_batch(param_list: List[Params], n_trials: int, exp_name: str) -> pd.DataFrame:
    print(f"\n🧪 Running {exp_name} ({len(param_list)} variations x {n_trials} trials)...")
    data = []
    total = len(param_list) * n_trials
    count = 0

    start = time.time()
    for p in param_list:
        for i in range(n_trials):
            data.append(run_single_trial(p, i))
            count += 1
            if count % 2000 == 0:
                print(f"   ... {count}/{total} done ({count/total:.1%})")

    df = pd.DataFrame(data)
    csv_path = os.path.join(OUTPUT_DIR, f"{exp_name}_raw.csv")
    df.to_csv(csv_path, index=False)
    print(f"✅ {exp_name} completed in {time.time()-start:.1f}s. Saved to {csv_path}")
    return df

# 1. Base Error Sweep
def exp_base_error_sweep():
    errors = [0.045, 0.0475, 0.05, 0.0525, 0.055, 0.0575, 0.06, 0.0625]
    params = [Params(base_error=e, res_width=0.05, power=4.0) for e in errors]
    df = run_experiment_batch(params, 2000, "1_BaseErrorSweep")

    # Plot
    plt.figure(figsize=(8,5))
    sns.lineplot(data=df, x="base_error", y="success", marker="o", color="#00ffcc")
    plt.title("Critical Phase Transition: Base Error Rate")
    plt.grid(True, alpha=0.2)
    plt.savefig(os.path.join(OUTPUT_DIR, "plot_1_error_sweep.png"))
    plt.close()

# 2. Resonance Width & Power
def exp_resonance_physics():
    widths = [0.02, 0.05, 0.08, 0.10, 0.15]
    powers = [3.0, 3.5, 4.0]
    params = []
    for p in powers:
        for w in widths:
            params.append(Params(base_error=0.06, res_width=w, power=p)) # Fix error at critical 0.06

    df = run_experiment_batch(params, 1000, "2_ResonancePhysics")

    # Plot
    plt.figure(figsize=(8,5))
    sns.lineplot(data=df, x="width", y="success", hue="power", marker="o", palette="viridis")
    plt.title("Resonance Sensitivity: Width vs Power")
    plt.grid(True, alpha=0.2)
    plt.savefig(os.path.join(OUTPUT_DIR, "plot_2_resonance.png"))
    plt.close()

# 3. Combined Grid (Heatmap)
def exp_combined_grid():
    errors = np.linspace(0.045, 0.065, 8)
    widths = np.linspace(0.03, 0.15, 8)
    params = []
    for e in errors:
        for w in widths:
            params.append(Params(base_error=e, res_width=w, power=4.0))

    df = run_experiment_batch(params, 1000, "3_CombinedGrid")

    # Pivot for Heatmap
    pivot = df.groupby(['base_error', 'width'])['success'].mean().unstack()

    plt.figure(figsize=(10,8))
    sns.heatmap(pivot, annot=True, fmt=".1%", cmap="magma")
    plt.title("Survival Landscape (Grid 8x8)")
    plt.gca().invert_yaxis() # Error increases upwards naturally in plots usually
    plt.savefig(os.path.join(OUTPUT_DIR, "plot_3_heatmap.png"))
    plt.close()

# 4. Long Run & Decomposition (The Deep Dive)
def exp_long_run_decomposition():
    # Точка в "Переходной зоне" (Balanced)
    p = Params(base_error=0.06, res_width=0.05, power=4.0)
    df = run_experiment_batch([p], 10000, "4_LongRun_DeepDive")

    # 4.1 Failure Reasons Pie Chart
    fails = df[df["success"] == 0]
    plt.figure(figsize=(6,6))
    fails["fail_reason"].value_counts().plot.pie(autopct='%1.1f%%', colors=['#ff9999', '#66b3ff', '#99ff99'])
    plt.title("Decomposition of Failure Causes (N=10k)")
    plt.ylabel("")
    plt.savefig(os.path.join(OUTPUT_DIR, "plot_4_fail_reasons.png"))
    plt.close()

    # 4.2 Scatter: Resonance vs Effective Error
    plt.figure(figsize=(10,6))
    # Sample 2000 points for readability
    sample = df.sample(min(2000, len(df)))

    plt.scatter(sample["reson_factor"], sample["eff_error"],
                c=sample["success"], cmap="coolwarm", alpha=0.6, s=15)
    plt.axhline(y=0.05, color='red', linestyle='--', label="Critical Threshold (0.05)")
    plt.xlabel("Resonance Factor (Fit to Field)")
    plt.ylabel("Effective Error Rate")
    plt.title("The Mechanism of Survival: Resonance vs Error")
    plt.colorbar(label="Success (1) / Fail (0)")
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_DIR, "plot_4_scatter_mechanism.png"))
    plt.close()

    # 4.3 Boxplot Invariant I
    plt.figure(figsize=(6,6))
    sns.boxplot(data=df, x="success", y="I", palette="Set2")
    plt.title("Topological Invariant I: Survivors vs Dead")
    plt.savefig(os.path.join(OUTPUT_DIR, "plot_4_invariant_boxplot.png"))
    plt.close()

    # Stats Report
    stats = {
        "success_rate": df["success"].mean(),
        "std_success": df["success"].std(),
        "median_eff_error": df["eff_error"].median(),
        "fraction_protected": (df["eff_error"] < 0.05).mean()
    }
    print("\n📜 LONG RUN STATS:")
    print(stats)

# --- MAIN RUNNER ---
if __name__ == "__main__":
    plt.style.use('dark_background')
    print("🚀 STARTING COMPREHENSIVE ENGEL STUDY...")

    exp_base_error_sweep()
    exp_resonance_physics()
    exp_combined_grid()
    exp_long_run_decomposition()

    print("\n✅ ALL EXPERIMENTS COMPLETED. CHECK 'engel_comprehensive_lab' FOLDER.")

