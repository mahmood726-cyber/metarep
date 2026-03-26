"""
MetaRep — Generate publication-ready figures from Pairwise70 pipeline results.
Produces 4 PDF + PNG figures for the JAMA manuscript.

Usage: python generate_figures.py
"""
import platform
platform._wmi_query = lambda *a, **k: ('10.0.26100', 1, 'Multiprocessor Free', 0, 0)

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

OUT_DIR = os.path.join(os.path.dirname(__file__), 'figures')
DATA = os.path.join(os.path.dirname(__file__), 'data', 'rep_prob_all.csv')
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA)
sig = df[df['significant'] == True].copy()

print(f"Total reviews: {len(df)}")
print(f"Significant: {len(sig)} ({100*len(sig)/len(df):.1f}%)")
print(f"Median P(rep) among significant: {sig['p_rep'].median()*100:.1f}%")

# Style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# ═══════════════════════════════════════════════════════════════
# FIGURE 1: Histogram of P(replication) among significant MAs
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))
bins = np.arange(0, 1.05, 0.05)
counts, _, patches = ax.hist(sig['p_rep'], bins=bins, color='#3b82f6', edgecolor='white', linewidth=0.5)

# Color bins below 50% red
for i, (patch, left_edge) in enumerate(zip(patches, bins[:-1])):
    if left_edge + 0.025 < 0.50:
        patch.set_facecolor('#ef4444')

ax.axvline(x=sig['p_rep'].median(), color='#1e3a5f', linewidth=2, linestyle='--',
           label=f'Median: {sig["p_rep"].median()*100:.1f}%')
ax.axvline(x=0.50, color='#f59e0b', linewidth=1.5, linestyle=':',
           label='50% threshold')
ax.axvline(x=0.80, color='#10b981', linewidth=1.5, linestyle=':',
           label='80% threshold')

ax.set_xlabel('Replication Probability')
ax.set_ylabel('Number of Meta-Analyses')
ax.set_title(f'Replication Probability Among {len(sig)} Significant Cochrane Meta-Analyses')
ax.xaxis.set_major_formatter(PercentFormatter(xmax=1))
ax.legend(loc='upper right', fontsize=9)

# Annotation
below50 = (sig['p_rep'] < 0.50).sum()
ax.annotate(f'{below50}/{len(sig)} ({100*below50/len(sig):.0f}%) < 50%',
            xy=(0.25, max(counts)*0.85), fontsize=10, fontweight='bold', color='#ef4444',
            ha='center')

fig.savefig(os.path.join(OUT_DIR, 'figure1_rep_prob_histogram.pdf'))
fig.savefig(os.path.join(OUT_DIR, 'figure1_rep_prob_histogram.png'))
plt.close(fig)
print("Figure 1: histogram saved")

# ═══════════════════════════════════════════════════════════════
# FIGURE 2: P(rep) vs I² scatter
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 5))
colors = ['#3b82f6' if s else '#94a3b8' for s in sig['significant']]
ax.scatter(sig['i2'], sig['p_rep'] * 100, alpha=0.5, s=20, c='#3b82f6', edgecolors='none')

# Lowess trend
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    sorted_data = sig[['i2', 'p_rep']].dropna().sort_values('i2')
    trend = lowess(sorted_data['p_rep'] * 100, sorted_data['i2'], frac=0.4)
    ax.plot(trend[:, 0], trend[:, 1], color='#dc2626', linewidth=2.5, label='LOWESS trend')
except ImportError:
    # Fallback: simple binned means
    for lo in range(0, 100, 10):
        subset = sig[(sig['i2'] >= lo) & (sig['i2'] < lo + 10)]
        if len(subset) >= 3:
            ax.plot(lo + 5, subset['p_rep'].mean() * 100, 'o', color='#dc2626', markersize=6)

ax.axhline(y=50, color='#f59e0b', linewidth=1, linestyle=':', alpha=0.7)
ax.axhline(y=80, color='#10b981', linewidth=1, linestyle=':', alpha=0.7)

ax.set_xlabel('I² (%)')
ax.set_ylabel('Replication Probability (%)')
ax.set_title('Replication Probability vs Heterogeneity (Significant MAs)')
ax.set_xlim(-2, 100)
ax.set_ylim(-2, 105)
ax.legend(loc='upper right', fontsize=9)

fig.savefig(os.path.join(OUT_DIR, 'figure2_rep_vs_i2.pdf'))
fig.savefig(os.path.join(OUT_DIR, 'figure2_rep_vs_i2.png'))
plt.close(fig)
print("Figure 2: scatter saved")

# ═══════════════════════════════════════════════════════════════
# FIGURE 3: P(rep) vs k (number of studies)
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(sig['k'], sig['p_rep'] * 100, alpha=0.5, s=20, c='#8b5cf6', edgecolors='none')

# Binned means
k_bins = [(2, 5), (5, 10), (10, 20), (20, 50), (50, 200)]
for lo, hi in k_bins:
    subset = sig[(sig['k'] >= lo) & (sig['k'] < hi)]
    if len(subset) >= 3:
        ax.plot((lo + hi) / 2, subset['p_rep'].mean() * 100, 's', color='#dc2626',
                markersize=8, zorder=5)

ax.axhline(y=50, color='#f59e0b', linewidth=1, linestyle=':', alpha=0.7)
ax.set_xlabel('Number of Studies (k)')
ax.set_ylabel('Replication Probability (%)')
ax.set_title('Replication Probability vs Number of Studies (Significant MAs)')
ax.set_xscale('log')
ax.set_xlim(1.5, 200)
ax.set_ylim(-2, 105)

fig.savefig(os.path.join(OUT_DIR, 'figure3_rep_vs_k.pdf'))
fig.savefig(os.path.join(OUT_DIR, 'figure3_rep_vs_k.png'))
plt.close(fig)
print("Figure 3: rep vs k saved")

# ═══════════════════════════════════════════════════════════════
# FIGURE 4: Predictive vs Classical Power scatter
# ═══════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6, 6))

# Only plot reviews with tau2 > 0 (otherwise predictive = classical)
het = sig[sig['tau2'] > 0].copy()
no_het = sig[sig['tau2'] == 0].copy()

ax.scatter(no_het['p_classical'] * 100, no_het['p_rep'] * 100,
           alpha=0.4, s=15, c='#94a3b8', label=f'tau²=0 (n={len(no_het)})', edgecolors='none')
ax.scatter(het['p_classical'] * 100, het['p_rep'] * 100,
           alpha=0.5, s=20, c='#f97316', label=f'tau²>0 (n={len(het)})', edgecolors='none')

# Identity line
ax.plot([0, 100], [0, 100], 'k--', linewidth=1, alpha=0.5, label='y = x')

ax.set_xlabel('Classical Power (%)')
ax.set_ylabel('Predictive Power — MetaRep (%)')
ax.set_title('Classical vs Heterogeneity-Adjusted Replication Probability')
ax.set_xlim(-2, 105)
ax.set_ylim(-2, 105)
ax.set_aspect('equal')
ax.legend(loc='lower right', fontsize=9)

# Annotate the gap region
ax.fill_between([0, 100], [0, 100], [0, 0], alpha=0.05, color='red')
ax.text(70, 30, 'Overestimated\nby classical power', fontsize=9, color='#dc2626',
        ha='center', style='italic', alpha=0.7)

fig.savefig(os.path.join(OUT_DIR, 'figure4_predictive_vs_classical.pdf'))
fig.savefig(os.path.join(OUT_DIR, 'figure4_predictive_vs_classical.png'))
plt.close(fig)
print("Figure 4: predictive vs classical saved")

print(f"\nAll 4 figures saved to {OUT_DIR}/")
print("  figure1_rep_prob_histogram.pdf/png")
print("  figure2_rep_vs_i2.pdf/png")
print("  figure3_rep_vs_k.pdf/png")
print("  figure4_predictive_vs_classical.pdf/png")
