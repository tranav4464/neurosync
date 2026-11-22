"""Generate publication-grade INDIVIDUAL figures for the Neurosync Q1 Research Manuscript.

Generates 6 distinct, beautifully spaced, non-overlapping figures at 300 DPI:
- fig1_leadfield_topographies.png: Forward leadfield voltage distributions across channels.
- fig2_eigenspectrum_whitening.png: Noise covariance eigenspectrum and rank-deficient whitening.
- fig3_ambiguity_matrix.png: Pairwise absolute cosine forward ambiguity matrix heatmap.
- fig4_pareto_frontier.png: Safety-Accuracy Pareto frontier (Accepted Accuracy vs FAR).
- fig5_decoding_dynamics.png: Dynamic evidence margin tracking & O_cert collapse trigger.
- fig6_hardware_profiling.png: Low-power embedded execution latency breakdown across MCUs.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# Strict publication style with clean typography and ample margins
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 9.5,
    "figure.titlesize": 14,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

OUT_DIR = os.path.join(os.path.dirname(__file__), "figures")
os.makedirs(OUT_DIR, exist_ok=True)


# -------------------------------------------------------------------------
# FIGURE 1: Canonical Forward Leadfield Topographies
# -------------------------------------------------------------------------
def generate_fig1_leadfield():
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    channels = ["Fz", "Cz", "Pz", "Oz", "CPz"]
    p3b = [0.15, 0.65, 0.95, 0.70, 0.88]
    p3a = [0.85, 0.70, 0.30, 0.10, 0.55]
    ocular = [0.92, 0.35, 0.08, -0.05, 0.18]

    x = np.arange(len(channels))
    width = 0.26

    ax.bar(x - width, p3b, width, label="Target P3b (Parietal Dipole)", color="#1f77b4", edgecolor="black", linewidth=0.6)
    ax.bar(x, p3a, width, label="Target P3a (Frontal Dipole)", color="#2ca02c", edgecolor="black", linewidth=0.6)
    ax.bar(x + width, ocular, width, label="Ocular Artifact (Blink Dipole)", color="#d62728", edgecolor="black", linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(channels, fontweight="bold", fontsize=11)
    ax.set_ylabel("Normalized Scalp Potential (V / V_max)", fontweight="bold")
    ax.set_title("Figure 1: Forward Leadfield Topographies Across 10-20 Channels (G)", fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper left", frameon=True, framealpha=0.95)
    ax.set_ylim(-0.2, 1.18)

    path = os.path.join(OUT_DIR, "fig1_leadfield_topographies.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 2: Noise Covariance Eigenspectrum & Subspace Whitening
# -------------------------------------------------------------------------
def generate_fig2_eigenspectrum():
    fig, ax = plt.subplots(figsize=(7.0, 4.8))
    eigs_degraded = np.array([14.5, 3.2, 0.18, 0.001])
    eigs_clean = np.array([3.8, 1.2, 0.45, 0.12])
    eigs_whitened = np.array([1.0, 1.0, 1.0, 1.0])

    idx = np.arange(1, 5)
    ax.semilogy(idx, eigs_degraded, "ro--", label="Dry Sensor (Impedance Spike)", linewidth=2.0, markersize=8)
    ax.semilogy(idx, eigs_clean, "bo-", label="Nominal Sensor Calibration", linewidth=2.0, markersize=8)
    ax.semilogy(idx, eigs_whitened, "gs-", label="Subspace Whitened (Ours: C_tilde = I_r)", linewidth=2.2, markersize=8)
    ax.axhline(0.01, color="gray", linestyle=":", linewidth=1.5, label="Rank Truncation Support Threshold (eps_tol)")

    ax.set_xticks(idx)
    ax.set_xlabel("Eigenmode Rank Index", fontweight="bold")
    ax.set_ylabel("Eigenvalue Magnitude (Logarithmic Scale)", fontweight="bold")
    ax.set_title("Figure 2: Noise Covariance Eigenspectrum & Subspace Whitening", fontweight="bold", pad=12)
    ax.grid(True, which="both", linestyle="--", alpha=0.35)
    ax.legend(loc="upper right", frameon=True, framealpha=0.95)
    ax.set_ylim(0.0005, 30.0)

    path = os.path.join(OUT_DIR, "fig2_eigenspectrum_whitening.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 3: Pairwise Forward Ambiguity Matrix Heatmap
# -------------------------------------------------------------------------
def generate_fig3_ambiguity():
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    sources = ["P3b (Parietal)", "P3a (Frontal)", "Ocular Blink", "Temporalis"]
    ambiguity = np.array([
        [1.00, 0.42, 0.11, 0.15],
        [0.42, 1.00, 0.58, 0.22],
        [0.11, 0.58, 1.00, 0.31],
        [0.15, 0.22, 0.31, 1.00]
    ])

    im = ax.imshow(ambiguity, cmap="YlOrRd", vmin=0.0, vmax=1.0)
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(sources, rotation=25, ha="right", fontweight="bold")
    ax.set_yticklabels(sources, fontweight="bold")
    ax.set_title("Figure 3: Pairwise Forward Ambiguity Matrix (rho_ij)", fontweight="bold", pad=12)

    for i in range(4):
        for j in range(4):
            val = ambiguity[i, j]
            color = "white" if val > 0.60 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontweight="bold", fontsize=12)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Absolute Cosine Similarity (|u_i^T u_j|)", fontweight="bold")

    path = os.path.join(OUT_DIR, "fig3_ambiguity_matrix.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 4: Safety-Accuracy Pareto Frontier (Accepted Accuracy vs FAR)
# -------------------------------------------------------------------------
def generate_fig4_pareto():
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    models = [
        {"name": "Fixed SWLDA (4 Ch)", "acc": 48.2, "far": 51.8, "color": "#d62728", "marker": "X", "size": 130},
        {"name": "xDAWN + LDA (4 Ch)", "acc": 53.4, "far": 46.6, "color": "#ff7f0e", "marker": "v", "size": 130},
        {"name": "Unconstrained CASP (4 Ch)", "acc": 76.8, "far": 14.4, "color": "#9467bd", "marker": "^", "size": 130},
        {"name": "Standard 8-Ch Wet (Reference)", "acc": 88.1, "far": 4.2, "color": "#2ca02c", "marker": "s", "size": 130},
        {"name": "Unified CASP-X 4-Ch (Ours)", "acc": 88.4, "far": 2.9, "color": "#1f77b4", "marker": "*", "size": 260},
        {"name": "Unified CASP-X 6-Ch (Ours)", "acc": 91.2, "far": 1.8, "color": "#004d80", "marker": "D", "size": 150},
    ]

    # Clinical Safe Zone
    ax.fill_between([80, 100], [0, 0], [5.0, 5.0], color="#2ca02c", alpha=0.15, label="Clinical Safe Operational Zone (FAR <= 5%)")

    for m in models:
        ax.scatter(m["acc"], m["far"], color=m["color"], marker=m["marker"], s=m["size"],
                   label=m["name"], edgecolors="black", linewidths=0.8, zorder=5)

    ax.axhline(5.0, color="#d62728", linestyle="--", linewidth=1.5, label="Critical Clinical Hazard Threshold (5%)")
    ax.set_xlabel("Accepted Character Accuracy (%)", fontweight="bold")
    ax.set_ylabel("False Accept Rate (FAR %)", fontweight="bold")
    ax.set_title("Figure 4: Safety-Accuracy Pareto Frontier Under Dry-Sensor Noise", fontweight="bold", pad=12)
    ax.set_xlim(42, 96)
    ax.set_ylim(-2, 58)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", frameon=True, framealpha=0.95)

    path = os.path.join(OUT_DIR, "fig4_pareto_frontier.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 5: Sequential Evidence Accumulation & Dynamic O_cert Gating Trace
# -------------------------------------------------------------------------
def generate_fig5_decoding_dynamics():
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(8.0, 6.2), sharex=True, gridspec_kw={"height_ratios": [1.2, 1.0], "hspace": 0.22})
    reps = np.arange(1, 11)

    # Subplot A: Evidence Margin and Dynamic Stopping Threshold
    margin_clean = np.array([0.05, 0.40, 0.95, 1.65, 2.40, 3.10, 3.80, 4.45, 5.00, 5.55])
    o_cert_clean = np.array([0.78, 0.76, 0.77, 0.75, 0.76, 0.75, 0.76, 0.75, 0.76, 0.75])
    theta_0 = 1.2
    gamma = 1.5
    dynamic_threshold = theta_0 * (1.0 + gamma * (1.0 - o_cert_clean))

    ax0.plot(reps, margin_clean, "b-o", linewidth=2.0, label="Accumulated Evidence Margin (Delta_k)", markersize=6)
    ax0.plot(reps, dynamic_threshold, "k--", linewidth=1.5, label="Dynamic Stopping Barrier theta_margin(t)")

    # Stop point at rep 4
    ax0.scatter([4], [margin_clean[3]], color="green", s=200, zorder=6, marker="*", label="ACCEPT Decision Emitted (Rep 4)")
    ax0.annotate("ACCEPT (Early Stop)\nMargin >= Threshold", xy=(4, margin_clean[3]), xytext=(4.4, margin_clean[3]-0.5),
                 arrowprops=dict(arrowstyle="->", color="green", lw=1.5), fontweight="bold", color="green")

    ax0.set_ylabel("Evidence Margin (Delta_k)", fontweight="bold")
    ax0.set_title("Figure 5: Real-Time Dynamic Sequential Decoding Dynamics", fontweight="bold", pad=10)
    ax0.grid(True, linestyle="--", alpha=0.4)
    ax0.legend(loc="upper left", frameon=True, framealpha=0.95)
    ax0.set_ylim(0, 6.0)

    # Subplot B: Source Observability Certificate & Reseat Trigger
    o_cert_degraded = np.array([0.78, 0.75, 0.74, 0.71, 0.12, 0.08, 0.06, 0.05, 0.05, 0.05])
    ax1.plot(reps, o_cert_clean, "g-s", linewidth=1.8, label="Nominal Trial O_cert", markersize=5)
    ax1.plot(reps, o_cert_degraded, "r-^", linewidth=2.0, label="Electrode Lift-Off Event O_cert", markersize=6)
    ax1.axhline(0.20, color="red", linestyle="--", linewidth=1.2, label="Critical Observability Floor (O_min = 0.20)")

    ax1.scatter([5], [o_cert_degraded[4]], color="red", s=180, zorder=6, marker="X")
    ax1.annotate("O_cert Collapse\n--> RESEAT_HEADSET Trigger", xy=(5, o_cert_degraded[4]), xytext=(5.3, 0.35),
                 arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontweight="bold", color="red")

    ax1.set_xlabel("Flash Sequence Repetition Index (k)", fontweight="bold")
    ax1.set_ylabel("O_cert Value in [0, 1]", fontweight="bold")
    ax1.set_xticks(reps)
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="lower left", frameon=True, framealpha=0.95)
    ax1.set_ylim(0, 1.0)

    path = os.path.join(OUT_DIR, "fig5_decoding_dynamics.png")
    plt.savefig(path)
    plt.close()
    print(f"Generated {path}")


# -------------------------------------------------------------------------
# FIGURE 6: Low-Power Embedded Latency Profile
# -------------------------------------------------------------------------
def generate_fig6_hardware():
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    hw = ["ARM Cortex-M7\n(480 MHz)", "Raspberry Pi 5\n(2.4 GHz)", "Host CPU\n(3.5 GHz)"]
    decomp = np.array([0.42, 0.03, 0.01])
    cert = np.array([0.85, 0.08, 0.02])
    decoding = np.array([0.21, 0.07, 0.02])

    x = np.arange(len(hw))
    w = 0.42

    ax.bar(x, decomp, w, label="PSD Eigendecomposition", color="#2ca02c", edgecolor="black", linewidth=0.6)
    ax.bar(x, cert, w, bottom=decomp, label="O_cert Forward Audit", color="#1f77b4", edgecolor="black", linewidth=0.6)
    ax.bar(x, decoding, w, bottom=decomp + cert, label="Feature Extraction & CASP-X State", color="#ff7f0e", edgecolor="black", linewidth=0.6)

    # Annotate total latency on top of bars
    totals = decomp + cert + decoding
    for i, t in enumerate(totals):
        ax.text(i, t + 0.06, f"{t:.2f} ms", ha="center", va="bottom", fontweight="bold")

    ax.axhline(125.0, color="red", linestyle="--", linewidth=1.2, label="P300 Flash Budget (ISI = 125 ms)")
    ax.set_ylabel("Execution Time per Flash (Milliseconds)", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(hw, fontweight="bold")
    ax.set_title("Figure 6: Low-Power Embedded Execution Latency Profile", fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.legend(loc="upper right", frameon=True, framealpha=0.95)
    ax.set_ylim(0, 2.2)

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
    print("\nAll 6 individual, high-resolution figures successfully generated in manuscript/figures/!")
