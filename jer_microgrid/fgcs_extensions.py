from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

from .config import SiteConfig, SyntheticConfig
from .controllers import build_controller
from .metrics import compute_group_metrics
from .network_sim import NetworkConfig, inject_network_state
from .simulation import attach_profile_columns, simulate_controller
from .synth import generate_dataset
from .utils import ensure_dir

def run_fgcs_robustness_audit(output_dir: str | Path = 'outputs_fgcs_extensions') -> pd.DataFrame:
    repo_root = Path.cwd()
    outdir = ensure_dir(repo_root / output_dir)
    
    site = SiteConfig()
    synth = SyntheticConfig(hours=24)
    # Generate base profiles
    dataset = generate_dataset([0, 1], site, synth)
    
    cases = [
        {'label': 'Ideal', 'disconnect_prob': 0.0},
        {'label': 'Low_Disruption', 'disconnect_prob': 0.02},
        {'label': 'High_Disruption', 'disconnect_prob': 0.10},
    ]
    
    results = []
    
    for case in cases:
        net_cfg = NetworkConfig(disconnect_prob_per_hr=case['disconnect_prob'])
        
        for controller_name in ['Proposed', 'GR', 'LinearMPCQPController']:
            if controller_name == 'LinearMPCQPController':
                try:
                    from .optimization_refs import LinearMPCQPController, WeightTuple
                    from .config import OptimConfig
                    optim = OptimConfig()
                    weights = WeightTuple(0.1, 0.1, 0.1)
                    ctrl_instance = LinearMPCQPController(site, optim, weights)
                except Exception as e:
                    print(f"Skipping MPC due to: {e}")
                    continue
            else:
                ctrl_instance = build_controller(controller_name, site)
            
            # Apply network injection to each profile individually to maintain structure
            profile_blocks = []
            for _, profile in dataset.groupby(['scenario', 'seed']):
                net_profile = inject_network_state(profile, int(profile['seed'].iloc[0]), net_cfg, site.ts_hours)
                
                sim_res = simulate_controller(net_profile, ctrl_instance, site, future_preview=True)
                tick = attach_profile_columns(sim_res.series, net_profile)
                tick['controller'] = controller_name
                tick['case'] = case['label']
                profile_blocks.append(tick)
            
            if not profile_blocks:
                continue
                
            tick_df = pd.concat(profile_blocks, ignore_index=True)
            metrics_df = compute_group_metrics(tick_df, site, ['controller', 'case', 'scenario', 'seed'])
            results.append(metrics_df)
            
    if not results:
        return pd.DataFrame()
        
    final_df = pd.concat(results, ignore_index=True)
    summary = final_df.groupby(['case', 'controller']).mean(numeric_only=True).reset_index()
    summary.to_csv(outdir / 'fgcs_robustness_summary.csv', index=False)
    
    return summary

def main():
    parser = argparse.ArgumentParser(description='Run FGCS Edge vs Cloud robustness experiments.')
    parser.add_argument('--output-dir', type=str, default='outputs_fgcs_extensions')
    args = parser.parse_args()
    run_fgcs_robustness_audit(args.output_dir)

if __name__ == '__main__':
    main()
