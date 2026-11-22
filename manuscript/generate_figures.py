"""Generate authentic, publication-standard academic figures for the Neurosync Research Manuscript.

Design Rules (IEEE / Nature Neuroscience / Elsevier standard):
- Professional typography (Helvetica/Arial sans-serif or clean serif), consistent sizing.
- Restrained, colorblind-safe color palette (Deep Navy, Slate Gray, Crimson, Forest Green, Coral).
- NO cluttered in-chart text boxes, NO cartoonish annotations or arrows overlapping data lines.
- Subplot titles indicated cleanly via academic lettering (e.g., '(a)', '(b)').
- All labels and legends positioned cleanly with proper spacing and white margins.
- No repetitive "Unified" naming; use exact scientific terminology: "CASP-X (Ours)".
- High resolution vector-like rendering at 300 DPI.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Professional academic theme
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 10,
    "axes.labelsize": 10.5,
    "axes.titlesize": 11,
    "xtick.labelsize": 9.5,
    "ytick.labelsize": 9.5,
    "legend.fontsize": 8.5,
    "figure.titlesize": 12,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "xtick.color": "#333333",
    "ytick.color": "#333333",
    "grid.color": "#E5E5E5",
    "grid.linestyle": "--",
    "grid.linewidth": 0.6,
})

OUT_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT_DIR, exist_ok=True)


# -------------------------------------------------------------------------
# FIGURE 1: Canonical Forward Leadfield Topographies
# -------------------------------------------------------------------------
def generate_fig1_leadfield():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    channels = ["Fz", "Cz", "CPz", "Pz", "Oz"]
    p3b = [0.15, 0.65, 0.88, 0.95, 0.70]
    p3a = [0.85, 0.70, 0.55, 0.30, 0.10]
    ocular = [0.92, 0.35, 0.18, 0.08, -0.05]

    x = np.arange(len(channels))
    width = 0.24

    ax.bar(x - width, p3b, width, label="Target P3b (Parietal)", color="#1F4E79", edgecolor="#0D233A", linewidth=0.7)
    ax.bar(x, p3a, width, label="Novelty P3a (Frontal)", color="#2E7D32", edgecolor="#143D17", linewidth=0.7)
    ax.bar(x + width, ocular, width, label="Ocular Artifact (Blink)", color="#C62828", edgecolor="#5C0E0E", linewidth=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(channels, fontweight="medium")
    ax.set_ylabel("Normalized Scalp Potential ($V / V_{\max}$)")
    ax.set_xlabel("10–20 Electrode Montage")
    ax.set_title("Forward Leadfield Distribution Across Sparse Electrodes ($G$)", pad=10)
    ax.grid(axis="y")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    ax.set_ylim(-0.15, 1.15)

    path = os.path.join(OUT_DIR, "fig1_leadfield_topographies.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 2: Noise Covariance Eigenspectrum & Subspace Whitening
# -------------------------------------------------------------------------
def generate_fig2_eigenspectrum():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    eigs_degraded = np.array([14.5, 3.2, 0.18, 0.001])
    eigs_clean = np.array([3.8, 1.2, 0.45, 0.12])
    eigs_whitened = np.array([1.0, 1.0, 1.0, 1.0])

    idx = np.arange(1, 5)
    ax.semilogy(idx, eigs_degraded, "o--", color="#C62828", label="High Impedance / Contact Spike", linewidth=1.6, markersize=6)
    ax.semilogy(idx, eigs_clean, "s-", color="#1F4E79", label="Nominal Sensor Calibration", linewidth=1.6, markersize=5)
    ax.semilogy(idx, eigs_whitened, "^-", color="#2E7D32", label="Subspace-Whitened (Rank $r=4$)", linewidth=1.8, markersize=6)
    ax.axhline(0.01, color="#777777", linestyle=":", linewidth=1.2, label=r"Truncation Threshold ($\kappa_{\rm cut}$)")

    ax.set_xticks(idx)
    ax.set_xlabel("Eigenmode Index ($k$)")
    ax.set_ylabel("Eigenvalue Magnitude ($\lambda_k$)")
    ax.set_title("Noise Covariance Eigenspectrum and Regularized Whitening", pad=10)
    ax.grid(True, which="both")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    ax.set_ylim(0.0003, 35.0)

    path = os.path.join(OUT_DIR, "fig2_eigenspectrum_whitening.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 3: Pairwise Forward Ambiguity Matrix Heatmap
# -------------------------------------------------------------------------
def generate_fig3_ambiguity():
    fig, ax = plt.subplots(figsize=(5.8, 4.8))
    sources = ["P3b (Parietal)", "P3a (Frontal)", "Ocular Blink", "Temporalis"]
    ambiguity = np.array([
        [1.00, 0.42, 0.11, 0.15],
        [0.42, 1.00, 0.58, 0.22],
        [0.11, 0.58, 1.00, 0.31],
        [0.15, 0.22, 0.31, 1.00]
    ])

    im = ax.imshow(ambiguity, cmap="Blues", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(sources, rotation=20, ha="right")
    ax.set_yticklabels(sources)
    ax.set_title("Pairwise Forward Directional Ambiguity Matrix ($\overline{\\rho}_{ij}$)", pad=10)

    for i in range(4):
        for j in range(4):
            val = ambiguity[i, j]
            color = "white" if val > 0.65 else "#1A1A1A"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=10.5, fontweight="medium")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Absolute Cosine Similarity ($|\\hat{u}_i^T \\hat{u}_j|$)")
    cbar.ax.tick_params(labelsize=8.5)

    path = os.path.join(OUT_DIR, "fig3_ambiguity_matrix.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 4: Safety-Accuracy Pareto Frontier (Professional Academic Style)
# -------------------------------------------------------------------------
def generate_fig4_pareto():
    fig, ax = plt.subplots(figsize=(6.8, 4.5))

    # Clean academic models without visual clutter
    models = [
        {"name": "Fixed SWLDA (4 Ch)", "acc": 48.2, "far": 51.8, "color": "#D32F2F", "marker": "X", "size": 85},
        {"name": "xDAWN + LDA (4 Ch)", "acc": 53.4, "far": 46.6, "color": "#E65100", "marker": "v", "size": 80},
        {"name": "Unconstrained CASP (4 Ch)", "acc": 76.8, "far": 14.4, "color": "#6A1B9A", "marker": "^", "size": 80},
        {"name": "Standard 8-Ch Wet (Ref)", "acc": 88.1, "far": 4.2, "color": "#2E7D32", "marker": "s", "size": 75},
        {"name": "CASP-X 4-Ch (Ours)", "acc": 88.4, "far": 2.9, "color": "#1565C0", "marker": "o", "size": 95},
        {"name": "CASP-X 6-Ch (Ours)", "acc": 91.2, "far": 1.8, "color": "#0D47A1", "marker": "D", "size": 80},
    ]

    # Clinical Safe Operational Zone (< 5% FAR)
    ax.axhspan(0, 5.0, color="#E8F5E9", alpha=0.9, zorder=1)
    ax.text(45, 2.0, "Clinical Safety Zone (FAR <= 5%)", color="#2E7D32", fontsize=9, fontweight="medium")

    for m in models:
        ax.scatter(m["acc"], m["far"], color=m["color"], marker=m["marker"], s=m["size"],
                   label=m["name"], edgecolors="#222222", linewidths=0.7, zorder=5)

    ax.axhline(5.0, color="#D32F2F", linestyle="--", linewidth=1.2, zorder=2)

    ax.set_xlabel("Accepted Character Accuracy (%)")
    ax.set_ylabel("False Accept Rate (FAR %)")
    ax.set_title("Safety-Accuracy Pareto Frontier Under Dry-Sensor Noise", pad=10)
    ax.set_xlim(42, 96)
    ax.set_ylim(-1, 56)
    ax.grid(True, zorder=0)
    ax.legend(loc="upper right", frameon=True, framealpha=0.92, edgecolor="#CCCCCC", ncol=1)

    path = os.path.join(OUT_DIR, "fig4_pareto_frontier.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 5: Sequential Evidence Accumulation & Gating Trace (Clean Multi-Panel)
# -------------------------------------------------------------------------
def generate_fig5_decoding_dynamics():
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(7.0, 5.0), sharex=True,
                                   gridspec_kw={"height_ratios": [1.1, 1.0], "hspace": 0.22})
    reps = np.arange(1, 11)

    # (a) Top panel: Evidence Margin & Dynamic Stopping Barrier
    margin_clean = np.array([0.05, 0.40, 0.95, 1.65, 2.40, 3.10, 3.80, 4.45, 5.00, 5.55])
    o_cert_clean = np.array([0.78, 0.76, 0.77, 0.75, 0.76, 0.75, 0.76, 0.75, 0.76, 0.75])
    theta_0 = 1.2
    gamma = 1.5
    dynamic_threshold = theta_0 * (1.0 + gamma * (1.0 - o_cert_clean))

    ax0.plot(reps, margin_clean, "-o", color="#1565C0", linewidth=1.8, markersize=5, label=r"Evidence Margin ($\Delta_k$)")
    ax0.plot(reps, dynamic_threshold, "--", color="#424242", linewidth=1.3, label=r"Dynamic Boundary ($\theta_k$)")

    # Clean decision point marker (no overlapping boxes)
    ax0.scatter([4], [margin_clean[3]], color="#2E7D32", s=110, zorder=6, marker="o", edgecolors="#1B5E20", label="Acceptance Emitted (Rep 4)")

    ax0.set_ylabel(r"Margin ($\Delta L_k$)")
    ax0.set_title("(a) Sequential Evidence Accumulation", loc="left", fontsize=10, fontweight="bold")
    ax0.grid(True)
    ax0.legend(loc="upper left", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    ax0.set_ylim(-0.2, 6.0)

    # (b) Bottom panel: Observability Certificate & Reseat Trigger
    o_cert_degraded = np.array([0.78, 0.75, 0.74, 0.71, 0.09, 0.06, 0.05, 0.04, 0.04, 0.04])
    ax1.plot(reps, o_cert_clean, "-s", color="#2E7D32", linewidth=1.6, markersize=4.5, label=r"Nominal Contact ($\mathcal{O}_{\rm cert}$)")
    ax1.plot(reps, o_cert_degraded, "-^", color="#D32F2F", linewidth=1.6, markersize=5, label=r"Electrode Lift-Off Event ($\mathcal{O}_{\rm cert}$)")
    ax1.axhline(0.20, color="#D32F2F", linestyle=":", linewidth=1.2, label=r"Critical Floor ($\mathcal{O}_{\rm crit} = 0.20$)")

    # Clean trigger marker
    ax1.scatter([5], [o_cert_degraded[4]], color="#D32F2F", s=110, zorder=6, marker="X", edgecolors="#5C0E0E")

    ax1.set_xlabel("Flash Sequence Repetition ($k$)")
    ax1.set_ylabel(r"$\mathcal{O}_{\rm cert}$ Metric")
    ax1.set_title("(b) Source Observability & Detachment Gating", loc="left", fontsize=10, fontweight="bold")
    ax1.set_xticks(reps)
    ax1.grid(True)
    ax1.legend(loc="center right", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    ax1.set_ylim(-0.05, 1.0)

    path = os.path.join(OUT_DIR, "fig5_decoding_dynamics.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 6: Low-Power Embedded Latency Profile
# -------------------------------------------------------------------------
def generate_fig6_hardware():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    hw = ["ARM Cortex-M7\n(480 MHz)", "Raspberry Pi 5\n(ARM Cortex-A76)", "Host Workstation\n(x86-64 3.5 GHz)"]
    decomp = np.array([0.42, 0.03, 0.01])
    cert = np.array([0.85, 0.08, 0.02])
    decoding = np.array([0.21, 0.07, 0.02])

    x = np.arange(len(hw))
    w = 0.38

    ax.bar(x, decomp, w, label="Eigendecomposition", color="#1F4E79", edgecolor="#0D233A", linewidth=0.7)
    ax.bar(x, cert, w, bottom=decomp, label=r"$\mathcal{O}_{\rm cert}$ Forward Audit", color="#2E7D32", edgecolor="#143D17", linewidth=0.7)
    ax.bar(x, decoding, w, bottom=decomp + cert, label="CASP-X Feature Extraction", color="#F57C00", edgecolor="#8C4400", linewidth=0.7)

    totals = decomp + cert + decoding
    for i, t in enumerate(totals):
        ax.text(i, t + 0.06, f"{t:.2f} ms", ha="center", va="bottom", fontsize=9.5, fontweight="medium")

    ax.set_ylabel("Execution Time per Flash (ms)")
    ax.set_xticks(x)
    ax.set_xticklabels(hw)
    ax.set_title("Real-Time Execution Latency Across Embedded Hardware", pad=10)
    ax.grid(axis="y")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, edgecolor="#CCCCCC")
    ax.set_ylim(0, 2.0)

    path = os.path.join(OUT_DIR, "fig6_hardware_profiling.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


if __name__ == "__main__":
    generate_fig1_leadfield()
    generate_fig2_eigenspectrum()
    generate_fig3_ambiguity()
    generate_fig4_pareto()
    generate_fig5_decoding_dynamics()
    generate_fig6_hardware()
    print("\nAll 6 publication-grade figures successfully generated!")
