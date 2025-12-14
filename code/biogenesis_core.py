import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List

# Set seed for reproducibility
rng = np.random.default_rng(42)

@dataclass
class Params:
    """Protobiogenesis Simulation Parameters (EnGeL Hypothesis)"""
    
    # --- Chemistry & Energy ---
    n_species: int = 20                # Number of molecule species in the primordial soup
    density: float = 0.6               # Reaction density (probability of interaction)
    energy_grad: float = 1.0           # Available energy gradient (Volcanism/UV)
    noise_level: float = 0.25          # Environmental entropy/noise level
    tidal_mod_amp: float = 0.2         # Tidal modulation amplitude (Tidal Pump)

    # --- Membrane Stability ---
    membrane_threshold: float = 0.55   # Threshold for retaining the cycle within the capsule
    membrane_leak: float = 0.15        # Leakage coefficient (connection decay)

    # --- Information Carrier (Proto-RNA) ---
    code_length: int = 64              # Code length (bits/nucleotides)
    alphabet: int = 4                  # Alphabet size (A, C, G, T)
    base_error_rate: float = 0.02      # Base replication error rate
    crit_error_threshold: float = 0.04 # Error catastrophe threshold (Eigen's limit)

    # --- Rhythms & Nested Eta (η) ---
    f_eta: float = 0.32                # Compression coefficient (Introversion constant)
    ext_periods: List[float] = None    # External periods: [Day, Month, Year...]
    resonance_tolerance: float = 0.08  # Resonance tolerance (phase matching precision)

    # --- Meta-Parameters ---
    trials: int = 500                  # Number of Monte Carlo trials
    mode: str = "no_field"             # Mode: "no_field" (Chaos) or "field" (EnGeL)

    def __post_init__(self):
        if self.ext_periods is None:
            # Arbitrary ticks: Day=1, Month~29.5, Core Node~8.5 years (~31025 ticks)
            self.ext_periods = [1.0, 29.5, 31025.0]


@dataclass
class Result:
    """Simulation Result Container"""
    success_rate: float                # Success percentage
    mean_cycle_coherence: float        # Mean cycle coherence
    mean_replication_fidelity: float   # Mean replication fidelity
    mean_invariant_I: float            # Stability invariant
    successes: int                     # Number of successful trials
    trials: int                        # Total trials
    mode: str                          # Simulation mode


def build_reaction_network(n: int, density: float) -> np.ndarray:
    """
    Builds a directed graph of chemical reactions.
    Adjacency matrix weights ~ transition probabilities.
    """
    adj = rng.random((n, n))
    mask = rng.random((n, n)) < density
    adj = adj * mask
    np.fill_diagonal(adj, 0.0)
    # Row normalization (sum of probabilities must be 1)
    row_sums = adj.sum(axis=1, keepdims=True) + 1e-12
    adj = adj / row_sums
    return adj


def evaluate_cycle_coherence(adj: np.ndarray, energy: float, leak: float, noise: float) -> Tuple[float, bool]:
    """
    Evaluate connectivity: does the network form a stable closed loop (autocatalysis).
    Returns: (coherence_coefficient, has_cycle)
    """
    n = adj.shape[0]
    # Spectral analysis: leading eigenvalues of the matrix
    eigvals = np.linalg.eigvals(adj)
    spectral_radius = np.max(np.abs(eigvals)).real
    
    # Distribution entropy (measure of chaos)
    p = adj + 1e-12
    entropy = -np.sum(p * np.log(p)) / n

    # Energy increases connectivity; leaks and noise decrease it
    coherence = spectral_radius * (1 + 0.6 * energy) - (0.4 * leak + 0.3 * noise)
    
    # Cycle strength: searching for "probability loops" (trace of matrix^3)
    loop_strength = np.mean(np.diag(np.linalg.matrix_power(adj + np.eye(n)*1e-6, 3)))
    
    # Cycle existence condition
    has_cycle = (coherence + 0.15 * entropy + 0.5 * loop_strength) > 0.85
    
    return float(coherence), bool(has_cycle)


def inner_period(ext_periods: List[float], f_eta: float, levels: int = 2) -> float:
    """
    Introversion Law: compressing external period into internal.
    T_int = T_ext * (eta ^ levels)
    """
    t_ints = []
    for T in ext_periods:
        t_ints.append(T * (f_eta ** levels))
    return float(np.mean(t_ints))


def resonance_score(T_internal: float, ext_periods: List[float], tol: float) -> float:
    """
    Resonance score: how close the internal clock is to integer multiples of external rhythms.
    1.0 = perfect resonance, 0.0 = total dissonance.
    """
    scores = []
    for T in ext_periods:
        # Find nearest integer multiple k
        k = max(1, int(round(T / T_internal)))
        # Mismatch error
        mismatch = abs((T / k) - T_internal) / (T + 1e-9)
        scores.append(max(0.0, 1.0 - mismatch / tol))
    return float(np.mean(scores))


def membrane_stability(base_threshold: float, energy_grad: float, noise: float) -> float:
    """
    Membrane stability (system boundary).
    Depends on energy gradient (nutrition) and destructive noise.
    """
    stability = base_threshold + 0.25 * energy_grad - 0.35 * noise
    return float(stability)


def replication_fidelity(code_length: int, alphabet: int, base_error: float, mod_factor: float) -> float:
    """
    Replication Fidelity (1 - error).
    mod_factor: improvement from resonance (EnGeL field suppresses errors).
    """
    # Error grows with code length but decreases with resonance
    effective_error = base_error * (1.0 + 0.5 * (code_length / 64.0)) * (1.0 - 0.6 * mod_factor)
    fidelity = max(0.0, 1.0 - effective_error)
    return float(fidelity)


def invariant_I(coherence: float, T_internal: float) -> float:
    """
    Stability Invariant I = Coherence / T_internal.
    Indicates "meaning density" per unit of time.
    """
    return float(coherence / (T_internal + 1e-9))


def run_trial(params: Params) -> Tuple[bool, Dict[str, float]]:
    """Run a single trial (one protocell)"""
    
    # 1. Build chemical network
    adj = build_reaction_network(params.n_species, params.density)

    # 2. Environment parameters (stochastic)
    energy = params.energy_grad * (1.0 + rng.normal(0.0, 0.1))
    noise = max(0.0, params.noise_level * (1.0 + rng.normal(0.0, 0.2)))
    leak = max(0.0, params.membrane_leak * (1.0 + rng.normal(0.0, 0.25)))

    # 3. Membrane
    mem_stab = membrane_stability(params.membrane_threshold, energy, noise)

    # 4. Rhythms:
    # No Field: internal rhythm is random, no resonance.
    # With Field: compression law (eta) and resonance are active.
    if params.mode == "no_field":
        T_int = max(0.05, rng.random() * 2.0)
        reson = 0.0
        mod_factor = 0.05
    else:
        T_int = inner_period(params.ext_periods, params.f_eta, levels=2)
        reson = resonance_score(T_int, params.ext_periods, params.resonance_tolerance)
        mod_factor = 0.2 + 0.6 * reson  # Field reinforces structure

    # 5. Coherence
    coherence, has_cycle = evaluate_cycle_coherence(adj, energy, leak, noise)

    # Condition: Cycle must be retained by the membrane
    holds = (mem_stab > 0.5) and has_cycle

    # 6. Code Replication
    fidelity = replication_fidelity(params.code_length, params.alphabet, params.base_error_rate, mod_factor)

    # Condition: Errors must not exceed the critical threshold
    error_ok = (1.0 - fidelity) < params.crit_error_threshold

    # Invariant
    Ival = invariant_I(coherence, T_int)

    # FINAL SUCCESS: Membrane holds + Cycle spins + Code copies
    success = bool(holds and error_ok)

    metrics = {
        "coherence": coherence,
        "fidelity": fidelity,
        "I": Ival,
        "membrane_stability": mem_stab,
        "T_internal": T_int,
        "resonance": reson
    }
    return success, metrics


def run_simulation(params: Params) -> Result:
    """Run a series of trials (Monte Carlo)"""
    successes = 0
    coh_list, fid_list, I_list = [], [], []
    
    for _ in range(params.trials):
        success, m = run_trial(params)
        if success:
            successes += 1
        coh_list.append(m["coherence"])
        fid_list.append(m["fidelity"])
        I_list.append(m["I"])
        
    sr = successes / params.trials
    
    return Result(
        success_rate=sr,
        mean_cycle_coherence=float(np.mean(coh_list)) if coh_list else 0.0,
        mean_replication_fidelity=float(np.mean(fid_list)) if fid_list else 0.0,
        mean_invariant_I=float(np.mean(I_list)) if I_list else 0.0,
        successes=successes,
        trials=params.trials,
        mode=params.mode
    )

# Quick test when running the file directly
if __name__ == "__main__":
    print("Running simulation core test...")
    res = run_simulation(Params(mode="field", trials=100))
    print(f"Mode: {res.mode}, Success Rate: {res.success_rate*100}%")