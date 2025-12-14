import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys

# Add current directory to path to import the core engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core engine (biogenesis_core.py)
try:
    from biogenesis_core import Params, run_simulation, inner_period
except ImportError:
    print("ERROR: biogenesis_core.py not found in code/ folder!")
    print("Ensure both files are in the same directory.")
    sys.exit(1)

# Setup paths for output
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
IMG_DIR = os.path.join(BASE_DIR, '..', 'images')

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMG_DIR, exist_ok=True)

def parameter_sweep():
    """
    Test 1: Parameter Stress Test.
    Comparing 'Chaos' (No Field) vs 'EnGeL' (Field) under harsh conditions.
    """
    print("\n--- Running Stress Test (Parameter Sweep) ---")
    results = []
    
    harder_params = [
        {"name": "High Noise", "noise_level": 0.5, "membrane_leak": 0.3},
        {"name": "Low Energy", "energy_grad": 0.5},
        {"name": "High Error Rate", "base_error_rate": 0.035, "crit_error_threshold": 0.04},
        {"name": "Hard Mode (Combined)", "noise_level": 0.4, "energy_grad": 0.6, "base_error_rate": 0.03},
    ]
    
    for i, mod in enumerate(harder_params):
        # Prepare parameters
        params_dict = {k: v for k, v in mod.items() if k != "name"}
        
        # 1. Run without field
        base_params = Params(mode="no_field", trials=300, **params_dict)
        r0 = run_simulation(base_params)
        
        # 2. Run with EnGeL field
        field_params = Params(mode="field", trials=300, **params_dict)
        r1 = run_simulation(field_params)
        
        results.append({
            "test_name": mod["name"],
            "no_field_success": r0.success_rate,
            "field_success": r1.success_rate,
            "improvement": r1.success_rate - r0.success_rate
        })
        print(f"  {mod['name']}: No Field={r0.success_rate:.2f} | With Field={r1.success_rate:.2f}")
        
    return results

def analyze_eta_effect():
    """
    Test 2: Finding the 'Golden Ratio'.
    Testing different Eta (η) values to find the survival peak.
    """
    print("\n--- Running Eta (η) Analysis ---")
    eta_values = [0.1, 0.2, 0.32, 0.4, 0.5, 0.618, 0.7, 0.9]
    results = []
    
    for eta in eta_values:
        # Using moderately hard conditions to see the difference
        params = Params(
            mode="field", 
            trials=200,
            f_eta=eta,
            noise_level=0.35,
            energy_grad=0.7
        )
        r = run_simulation(params)
        results.append({
            "eta": eta,
            "success_rate": r.success_rate,
            "coherence": r.mean_cycle_coherence
        })
        # print(f"  η={eta}: Success={r.success_rate:.2f}")
    return results

def analyze_periods():
    """
    Test 3: Planetary Resonance Check.
    Earth, Mars, Solar, and the hypothetical 'EnGeL Node'.
    """
    print("\n--- Analyzing External Periods (Planetary) ---")
    period_sets = [
        {"name": "Earth", "periods": [1.0, 29.5, 365.25]},
        {"name": "Mars", "periods": [1.03, 30.5, 687.0]},
        {"name": "Solar (22yr)", "periods": [1.0, 365.25, 8030.0]},
        {"name": "EnGeL (Node 8.5)", "periods": [1.0, 29.5, 3102.5]}, # Your Node!
    ]
    
    results = []
    for pset in period_sets:
        params = Params(
            mode="field",
            trials=200,
            ext_periods=pset["periods"],
            noise_level=0.35
        )
        r = run_simulation(params)
        results.append({
            "name": pset["name"],
            "success_rate": r.success_rate
        })
        print(f"  {pset['name']}: {r.success_rate:.2f}")
    return results

def visualize_dashboard(param_res, eta_res, period_res):
    """
    Generate final dashboard (4 plots).
    """
    print("\n--- Generating Plots... ---")
    plt.style.use('dark_background')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('EnGeL: Protobiogenesis Stability Analysis', fontsize=16, color='white')
    
    # 1. Mode Comparison (Bar Chart)
    ax1 = axes[0, 0]
    names = [r['test_name'] for r in param_res]
    x = np.arange(len(names))
    width = 0.35
    
    ax1.bar(x - width/2, [r['no_field_success'] for r in param_res], width, label='Chaos (No Field)', color='gray')
    ax1.bar(x + width/2, [r['field_success'] for r in param_res], width, label='Order (EnGeL)', color='#9467bd')
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=15)
    ax1.set_ylabel('Success Probability')
    ax1.set_title('Survival in Hostile Conditions')
    ax1.legend()
    ax1.grid(alpha=0.2)

    # 2. Eta Influence (Line Chart)
    ax2 = axes[0, 1]
    etas = [r['eta'] for r in eta_res]
    succ = [r['success_rate'] for r in eta_res]
    
    ax2.plot(etas, succ, 'o-', color='#2ca02c', linewidth=2)
    # Marking key points
    ax2.axvline(x=0.32, color='red', linestyle='--', label='η=0.32 (Modern)')
    ax2.axvline(x=0.618, color='gold', linestyle='--', label='η=0.618 (Golden)')
    ax2.set_xlabel('Eta (η)')
    ax2.set_ylabel('Success Probability')
    ax2.set_title('Resonance Efficiency of η')
    ax2.legend()
    ax2.grid(alpha=0.2)

    # 3. Periods (Bar Chart)
    ax3 = axes[1, 0]
    p_names = [r['name'] for r in period_res]
    p_vals = [r['success_rate'] for r in period_res]
    colors = ['#1f77b4', '#d62728', '#ff7f0e', '#e377c2']
    
    ax3.bar(p_names, p_vals, color=colors, alpha=0.8)
    ax3.set_ylim(0.8, 1.05) # Zoom to see differences
    ax3.set_title('Planetary Resonance Check')
    ax3.grid(alpha=0.2, axis='y')

    # 4. Phase Diagram (Heatmap)
    ax4 = axes[1, 1]
    noise_range = np.linspace(0.1, 0.6, 15)
    energy_range = np.linspace(0.5, 1.5, 15)
    grid = np.zeros((len(noise_range), len(energy_range)))
    
    # Fast run for heatmap
    for i, n in enumerate(noise_range):
        for j, e in enumerate(energy_range):
            p = Params(mode="field", trials=30, noise_level=n, energy_grad=e, f_eta=0.32)
            grid[i, j] = run_simulation(p).success_rate
            
    im = ax4.imshow(grid, extent=[0.5, 1.5, 0.6, 0.1], aspect='auto', cmap='magma')
    ax4.set_xlabel('Energy Gradient')
    ax4.set_ylabel('Noise Level')
    ax4.set_title('Phase Diagram (Field ON, eta=0.32)')
    plt.colorbar(im, ax=ax4, label='Success Probability')

    plt.tight_layout()
    
    # Save Image
    out_path = os.path.join(IMG_DIR, 'stress_test_dashboard.png')
    plt.savefig(out_path, dpi=150)
    print(f"Plot saved: {out_path}")

if __name__ == "__main__":
    # Run all tests
    p_res = parameter_sweep()
    e_res = analyze_eta_effect()
    per_res = analyze_periods()
    
    # Collect data into dictionary
    all_data = {
        "parameter_sweep": p_res,
        "eta_sweep": e_res,
        "period_analysis": per_res
    }
    
    # Save JSON
    json_path = os.path.join(DATA_DIR, 'stress_test_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved: {json_path}")
    
    # Visualization
    visualize_dashboard(p_res, e_res, per_res)