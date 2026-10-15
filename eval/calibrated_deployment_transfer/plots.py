"""Static scientific figures; no model fitting or result-based subset selection."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import *

def run():
    start('plots'); dst = OUT/'figures'; dst.mkdir(parents=True, exist_ok=True)
    d = pd.read_parquet(OUT/'diagnostics/classification-summary.parquet')
    k = pd.read_parquet(OUT/'diagnostics/kernel-feature-summary.parquet')
    for kind in ['post', 'pre']:
        a = d[d.kind.eq(kind)].pivot(index='source', columns='target', values='F1_all').loc[PROTOCOLS, PROTOCOLS]
        fig, ax = plt.subplots(figsize=(6, 5)); im = ax.imshow(a, vmin=0, vmax=1, cmap='viridis')
        ax.set_xticks(range(4), PROTOCOLS, rotation=30, ha='right'); ax.set_yticks(range(4), PROTOCOLS)
        ax.set_xlabel('Test deployment'); ax.set_ylabel('Training deployment'); ax.set_title(kind+' six-class macro F1')
        for i in range(4):
            for j in range(4): ax.text(j, i, f'{a.iloc[i,j]:.3f}', ha='center', va='center', color='white' if a.iloc[i,j] < .65 else 'black')
        fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(dst/(kind+'-transfer.png'), dpi=180); plt.close(fig)
    values = []
    for (source, target), part in k.groupby(['source', 'target']):
        values.append({'source': source, 'target': target, 'loss': float(np.dot(part.set_index('feature').loc[FEATURES].loss_bits, FEATURE_WEIGHTS))})
    a = pd.DataFrame(values).pivot(index='source', columns='target', values='loss').loc[PROTOCOLS, PROTOCOLS]
    fig, ax = plt.subplots(figsize=(6, 5)); im = ax.imshow(a, cmap='magma')
    ax.set_xticks(range(4), PROTOCOLS, rotation=30, ha='right'); ax.set_yticks(range(4), PROTOCOLS)
    ax.set_title('Source kernel conditional log-loss (bits)')
    for i in range(4):
        for j in range(4): ax.text(j, i, f'{a.iloc[i,j]:.3f}', ha='center', va='center', color='white')
    fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(dst/'kernel-transfer.png', dpi=180); plt.close(fig)
    contrasts = pd.read_parquet(OUT/'comparisons/primary-contrasts.parquet')
    fig, ax = plt.subplots(figsize=(7, 3)); y = np.arange(3)
    ax.hlines(y, contrasts.CI98_333_low, contrasts.CI98_333_high)
    ax.plot(contrasts.delta_F1_uncovered, y, 'o')
    ax.set_yticks(y, contrasts.comparison); ax.axvline(0, color='black', linestyle='--')
    ax.set_xlabel('Uncovered-class F1 difference; family-adjusted 98.333% CI')
    fig.tight_layout(); fig.savefig(dst/'primary-contrasts.png', dpi=180); plt.close(fig)
    d = pd.read_parquet(OUT/'scores/target-group-summary.parquet')
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey=True)
    for ax, proto in zip(axes.ravel(), PROTOCOLS):
        for arm in ARMS+['StrongPost', 'CT5']:
            a = d[d.target.eq(proto)&d.arm.eq(arm)].set_index('group').loc[list(MASKS)]
            ax.plot(range(3), a.F1_uncovered, marker='o', label=arm)
        ax.set_title(proto); ax.set_xticks(range(3), list(MASKS)); ax.set_ylim(0, 1); ax.set_ylabel('Uncovered-class F1')
    axes[0, 0].legend(fontsize=8, ncol=2); fig.tight_layout(); fig.savefig(dst/'twelve-scenarios.png', dpi=180); plt.close(fig)
    flips = pd.read_parquet(OUT/'scores/error-flips.parquet').groupby('comparator')[['repair', 'added_error']].sum()
    ax = flips.plot.bar(figsize=(8, 4)); ax.set_ylabel('Visits across masks (not independent samples)')
    ax.figure.tight_layout(); ax.figure.savefig(dst/'error-flips.png', dpi=180); plt.close(ax.figure)
    classes = pd.read_parquet(OUT/'scores/class-results.parquet').groupby(['arm', 'label_id'], as_index=False).F1.mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    for arm in ARMS+['StrongPost', 'CT5']:
        a = classes[classes.arm.eq(arm)].set_index('label_id').loc[LABELS]
        ax.plot(range(6), a.F1, marker='o', label=arm)
    ax.set_xticks(range(6), ['Bing search', 'MDN doc', 'GitHub repo', 'Wikipedia', 'YT search', 'YT playback'], rotation=20)
    ax.set_ylabel('Class F1; equal deployments and masks'); ax.set_ylim(0, 1); ax.legend(ncol=3)
    fig.tight_layout(); fig.savefig(dst/'class-results.png', dpi=180); plt.close(fig)
    support = pd.read_parquet(OUT/'scores/source-pre-support.parquet').groupby(['target', 'feature'], as_index=False).mean_zero_support_mass.mean()
    fig, ax = plt.subplots(figsize=(10, 5))
    for target in PROTOCOLS:
        a = support[support.target.eq(target)].set_index('feature').loc[FEATURES]
        ax.plot(range(10), a.mean_zero_support_mass, marker='o', label=target)
    ax.set_xticks(range(10), FEATURES, rotation=40, ha='right'); ax.set_ylabel('Source pre zero-support mass')
    ax.legend(); fig.tight_layout(); fig.savefig(dst/'source-pre-support.png', dpi=180); plt.close(fig)
    finish('plots', files=len(list(dst.glob('*.png'))))

if __name__ == '__main__': run()
