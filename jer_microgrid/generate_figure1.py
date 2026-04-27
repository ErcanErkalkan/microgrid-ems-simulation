"""
Generate Figure 1: Edge-Native Controller Runtime Path Diagram
Saves to manuscript/fig/runtime_path_diagram.pdf
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path

def draw_box(ax, x, y, w, h, label, sublabel=None,
             facecolor='#e8f4fd', edgecolor='#1890ff', textcolor='#0a3d6b',
             fontsize=10, radius=0.04):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=f"round,pad={radius}",
                         linewidth=1.8, edgecolor=edgecolor, facecolor=facecolor, zorder=3)
    ax.add_patch(box)
    if sublabel:
        ax.text(x, y + 0.055, label, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color=textcolor, zorder=4)
        ax.text(x, y - 0.06, sublabel, ha='center', va='center', fontsize=7.5,
                color='#555', style='italic', zorder=4)
    else:
        ax.text(x, y, label, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color=textcolor, zorder=4)

def draw_arrow(ax, x1, x2, y, color='#1890ff'):
    ax.annotate('', xy=(x2 - 0.02, y), xytext=(x1 + 0.02, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=2.0),
                zorder=5)

def main():
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5.5)
    ax.axis('off')

    # ── Outer boundary: Edge Node ──
    edge_rect = FancyBboxPatch((0.35, 0.5), 12.3, 4.5,
                               boxstyle="round,pad=0.15",
                               linewidth=2.5, edgecolor='#2f54eb',
                               linestyle='--', facecolor='#f0f5ff', zorder=1)
    ax.add_patch(edge_rect)
    ax.text(6.5, 4.8, '⚡  Edge-Native Supervisor  —  O(1) Execution per Tick',
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='#2f54eb', zorder=4)

    # ── Y positions ──
    main_y = 2.7

    # ── INPUT box ──
    draw_box(ax, 1.0, main_y, 1.5, 1.1,
             'IoT Meter\nInputs',
             sublabel='P_base(t), SOC(t)',
             facecolor='#f9f0ff', edgecolor='#722ed1', textcolor='#391085',
             fontsize=9)

    # ── Step 1: Forecast ──
    draw_box(ax, 2.95, main_y, 1.6, 1.1,
             '(1) Forecast  F',
             sublabel='Short-horizon\nimport/export stress',
             facecolor='#e6f7ff', edgecolor='#1890ff')

    # ── Step 2: Risk Extraction ──
    draw_box(ax, 4.95, main_y, 1.6, 1.1,
             '(2) Risk Ext.  E',
             sublabel='Current / Peak /\nNear-cap risk',
             facecolor='#e6f7ff', edgecolor='#1890ff')

    # ── Step 3: Reserve Shaping ──
    draw_box(ax, 6.95, main_y, 1.6, 1.1,
             '(3) Reserve  R',
             sublabel='Adaptive SOC\nbounds',
             facecolor='#e6f7ff', edgecolor='#1890ff')

    # ── Step 4: Priority Rules ──
    rules_x = 9.05
    draw_box(ax, rules_x, main_y, 1.6, 2.6,
             '(4) Fixed-Priority\nRules  P',
             facecolor='#fffbe6', edgecolor='#faad14', textcolor='#613400', fontsize=9)
    modes = ['PS', 'VF', 'PREP_CH', 'PREP_DIS', 'IDLE']
    mode_colors = ['#ff7a45', '#73d13d', '#40a9ff', '#9254de', '#bfbfbf']
    for i, (m, c) in enumerate(zip(modes, mode_colors)):
        badge = FancyBboxPatch((rules_x - 0.52, 1.1 + i*0.38), 1.04, 0.3,
                               boxstyle="round,pad=0.04",
                               linewidth=1, edgecolor=c,
                               facecolor=c+'33', zorder=5)
        ax.add_patch(badge)
        ax.text(rules_x, 1.25 + i*0.38, m, ha='center', va='center',
                fontsize=7.5, color=c, fontweight='bold', zorder=6)

    # ── Step 5: Clipping ──
    draw_box(ax, 11.1, main_y, 1.5, 1.1,
             '(5) Clipping  C',
             sublabel='SOC-safe &\nstep feasible',
             facecolor='#e6f7ff', edgecolor='#1890ff')

    # ── OUTPUT box ──
    draw_box(ax, 12.65, main_y, 1.0, 1.1,
             'P_cmd',
             sublabel='Bounded\ncommand',
             facecolor='#f6ffed', edgecolor='#52c41a', textcolor='#135200',
             fontsize=9)

    # ── Arrows between boxes ──
    arrow_pairs = [
        (1.75, 2.15),  # Input → Forecast
        (3.75, 4.15),  # Forecast → Risk
        (5.75, 6.15),  # Risk → Reserve
        (7.75, 8.25),  # Reserve → Rules
        (9.85, 10.35), # Rules → Clip
        (11.85, 12.15),# Clip → Output
    ]
    for x1, x2 in arrow_pairs:
        draw_arrow(ax, x1, x2, main_y)

    # ── Offline fallback path ──
    ax.annotate('', xy=(1.0, 1.2), xytext=(1.0, 0.85),
                arrowprops=dict(arrowstyle='->', color='#cf1322', lw=1.5, linestyle='dashed'))
    ax.text(1.0, 0.65, 'Network\nDropout', ha='center', va='center',
            fontsize=7.5, color='#cf1322', style='italic')
    ax.plot([1.0, 9.05], [0.85, 0.85], color='#cf1322', linewidth=1.5, linestyle='--', zorder=5)
    ax.annotate('', xy=(9.05, 1.15), xytext=(9.05, 0.85),
                arrowprops=dict(arrowstyle='->', color='#cf1322', lw=1.5, linestyle='dashed'))
    ax.text(5.0, 0.65, '[!] Cloud-MPC freezes -- holds last valid cmd | Edge continues',
            ha='center', va='center', fontsize=7.5, color='#cf1322')

    # ── Legend ──
    legend_elements = [
        mpatches.Patch(facecolor='#e6f7ff', edgecolor='#1890ff', label='Computation Stage'),
        mpatches.Patch(facecolor='#fffbe6', edgecolor='#faad14', label='Priority Rule Dispatcher'),
        mpatches.Patch(facecolor='#f9f0ff', edgecolor='#722ed1', label='IoT Input'),
        mpatches.Patch(facecolor='#f6ffed', edgecolor='#52c41a', label='Bounded Output'),
        Line2D([0], [0], color='#cf1322', linewidth=1.5, linestyle='--', label='Network-Dropout Path'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=7.5,
              framealpha=0.9, ncol=3, bbox_to_anchor=(1.0, 0.0))

    plt.tight_layout()
    out = Path('manuscript/fig/runtime_path_diagram.pdf')
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Figure 1 saved -> {out}")

if __name__ == '__main__':
    main()
