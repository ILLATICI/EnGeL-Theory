# -*- coding: utf-8 -*-
"""
EnGeΛ Theory Verification Tool 
-------------------------------------
Author: Aletheia Wayehiaor
Date: December 19, 2025
Source Data: NASA JPL Small-Body Database (Live API)

Description:
This script fetches the latest orbital data for Trans-Neptunian Objects (TNOs) 
and Centaurs from NASA JPL, filters them according to the EnGeΛ protocol, 
and analyzes their distribution relative to the hypothetical resonant step.

Parameters:
- Resonance Step (ΔR): 22.14 AU
- Min Aphelion (Q): 80.0 AU
- Min Observations: 15
"""

import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys

# --- CONFIGURATION (EnGeΛ v.18) ---
STEP_AU = 22.14       # Resonant Step
MIN_Q = 80.0          # Minimum Aphelion Distance
MIN_OBS = 15          # Quality Filter
TOLERANCE = 2.0       # Resonance Window (+/- AU)
API_URL = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"

def fetch_group_data(group_code):
    """Fetches data for a specific orbital class (TNO or CEN)."""
    print(f"📡 Connecting to NASA JPL API (Class: {group_code})...")
    params = {
        'fields': 'full_name,e,a,ad,n_obs_used',
        'sb-class': group_code,
        'sb-kind': 'a',
        'full-prec': 'true'
    }
    try:
        response = requests.get(API_URL, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"   -> Success. Retrieved {count} objects.")
            return data.get('data', [])
        else:
            print(f"   -> API Error {response.status_code} for {group_code}")
            return []
    except Exception as e:
        print(f"   -> Connection failed: {e}")
        return []

def run_engel_analysis():
    print("🚀 INITIALIZING EnGeΛ PROTOCOL (v.18)...")
    print("-" * 50)

    # 1. Fetch Data (Split Query Strategy to avoid API limits)
    tno_data = fetch_group_data('TNO')
    cen_data = fetch_group_data('CEN')
    raw_data = tno_data + cen_data
    
    if not raw_data:
        print("❌ Critical Error: No data retrieved from NASA.")
        return

    print(f"\n⚙️  Processing {len(raw_data)} raw objects...")
    
    valid_objects = []
    phases = []

    # 2. Filter & Calculate
    for row in raw_data:
        try:
            # Parse fields: 0:Name, 1:e, 2:a, 3:ad(Q), 4:n_obs
            name = row[0]
            if row[1] is None or row[2] is None: continue
            
            e = float(row[1])
            a = float(row[2])
            # Use 'ad' from NASA if available, else calc Q = a(1+e)
            Q = float(row[3]) if row[3] is not None else a * (1 + e)
            n_obs = int(row[4]) if row[4] is not None else 0

            # EnGeΛ Filter
            if Q >= MIN_Q and n_obs >= MIN_OBS:
                # Calculate Phase
                phase = Q % STEP_AU
                
                # Check Resonance Hit
                in_resonance = (phase <= TOLERANCE) or (phase >= STEP_AU - TOLERANCE)
                
                valid_objects.append({
                    'Designation': name,
                    'Aphelion_Q': round(Q, 4),
                    'Phase_AU': round(phase, 4),
                    'In_Resonance': in_resonance,
                    'Obs_Count': n_obs
                })
                phases.append(phase)
        except Exception:
            continue

    # 3. Generate Report
    df = pd.DataFrame(valid_objects)
    df = df.drop_duplicates(subset=['Designation']) # Safety check
    
    total_n = len(df)
    hits = df['In_Resonance'].sum()
    hit_rate = (hits / total_n) * 100 if total_n > 0 else 0

    print("\n" + "="*50)
    print(f"🏆 EnGeΛ VERDICT (Data: NASA JPL Live)")
    print("="*50)
    print(f"Objects Analyzed (Q>={MIN_Q}, Obs>={MIN_OBS}): {total_n}")
    print(f"Resonant Objects (Node ±{TOLERANCE} AU):     {hits}")
    print(f"Resonance Density:                       {hit_rate:.2f}%")
    print("-" * 50)
    
    # Save CSV
    csv_name = "engel_v18_results.csv"
    df.to_csv(csv_name, index=False)
    print(f"💾 Data saved to: {csv_name}")

    # 4. Visualization
    print("📊 Generating Phase Distribution Plot...")
    plt.style.use('dark_background')
    plt.figure(figsize=(12, 7))
    
    # Histogram
    sns.histplot(phases, bins=22, kde=True, color='#00ffcc', alpha=0.5, edgecolor='black')
    
    # Resonance Lines
    plt.axvline(0, color='white', linestyle='--', linewidth=2, label=f'Node Rn (0 / {STEP_AU})')
    plt.axvline(STEP_AU, color='white', linestyle='--', linewidth=2)
    plt.axvline(STEP_AU/2, color='red', linestyle=':', alpha=0.7, label='Gap Zone')
    
    # Annotations
    plt.title(f"Orbital Phase Distribution (EnGeΛ v.18)\nN={total_n} | Step={STEP_AU} AU", fontsize=14, color='white')
    plt.xlabel("Distance from Node Rn (AU)", fontsize=12, color='white')
    plt.ylabel("Object Count", fontsize=12, color='white')
    plt.xlim(0, STEP_AU)
    plt.legend()
    plt.grid(color='gray', linestyle=':', linewidth=0.5, alpha=0.3)
    
    plt.savefig("engel_distribution_v18.png", dpi=150)
    print("✅ Plot saved: engel_distribution_v18.png")
    plt.show()

if __name__ == "__main__":

    run_engel_analysis()
