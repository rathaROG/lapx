"""Plot recorded benchmark totals without running the solvers.

Read benchmark.md and write docs/benchmark_summary.png and .svg.
Run this script from any directory. Matplotlib is the only extra dependency.
"""

from decimal import Decimal
from pathlib import Path
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


ROOT = Path(__file__).resolve().parents[1]
SINGLE = {
    "lapjv": "lapjv", "lapjvx": "lapjvx", "lapjvxa": "lapjvxa",
    "lapjvc": "lapjvc", "lapjvs": "lapjvs", "lapjvsa": "lapjvsa",
    "lapjvr": "lapjvr", "lapjvh": "lapjvh", "scipy": "SciPy",
}
BATCH = {
    "lapx-batch-jvx": "lapjvx_batch", "lapx-batch-jvxa": "lapjvxa_batch",
    "lapx-batch-jvs": "lapjvs_batch", "lapx-batch-jvsa": "lapjvsa_batch",
    "lapx-batch-jvsa64": "lapjvsa_batch (f64)",
    "lapx-batch-jvr": "lapjvr_batch", "lapx-batch-jvh": "lapjvh_batch",
    "scipy-loop": "SciPy loop",
}
TRACKING = {
    "LAPX LAPJV": "lapjv", "LAPX LAPJVX": "lapjvx",
    "LAPX LAPJVC": "lapjvc", "LAPX LAPJVS": "lapjvs",
    "LAPX LAPJVR": "lapjvr", "LAPX LAPJVH": "lapjvh",
    "BASELINE SciPy": "SciPy",
}


def recorded_section(text, title):
    """Read one recorded result block from its details section."""
    start = text.index(title)
    return text[start:text.index("</details>", start)]


def add_times(rows, labels, totals):
    """Require one positive timing per selected solver in every case."""
    found = {}
    for name, milliseconds in rows:
        if name not in labels:
            continue
        if name in found:
            raise ValueError("Duplicate result for " + name)
        value = Decimal(milliseconds)
        if not value.is_finite() or value <= 0:
            raise ValueError("Invalid time for " + name)
        found[name] = value
    if set(found) != set(labels):
        raise ValueError("Missing results: " + str(set(labels) - set(found)))
    for name, value in found.items():
        totals[labels[name]] += value / 1000


def assignment_totals(section, labels):
    """Sum displayed milliseconds across the same cases for every solver."""
    cases = re.split(r"^### (?:Matrix|Dense|Sparse) ", section, flags=re.M)[1:]
    if not cases:
        raise ValueError("No assignment cases found")
    totals = dict.fromkeys(labels.values(), Decimal(0))
    for case in cases:
        rows = re.findall(
            r"^([a-z][\w-]*)\s+(?:✅ PASS|⭐ BASE)\s+([\d.]+)\s",
            case, flags=re.M,
        )
        add_times(rows, labels, totals)
    return totals, len(cases)


def tracking_totals(text):
    """Sum the more precise overall rankings across recorded thresholds."""
    cases = re.split(
        r"^# Benchmark with threshold \(cost_limit\) = [\d.]+$", text, flags=re.M,
    )[1:]
    if not cases:
        raise ValueError("No tracking thresholds found")
    totals = dict.fromkeys(TRACKING.values(), Decimal(0))
    expected_sizes = None
    for case in cases:
        sizes = set(re.findall(r"^(\d+x\d+)\s*\|", case, flags=re.M))
        if not sizes or (expected_sizes is not None and sizes != expected_sizes):
            raise ValueError("Tracking thresholds cover different sizes")
        expected_sizes = sizes
        rows = re.findall(
            r"^\s+\d+\.\s+(.+?)\s*:\s*([\d.]+) ms\s*\|", case, flags=re.M,
        )
        add_times(rows, TRACKING, totals)
    return totals, len(expected_sizes), len(cases)


def read_totals(text):
    """Return totals and workload counts from the recorded results."""
    single, single_count = assignment_totals(
        recorded_section(text, "Historical single results:"), SINGLE,
    )
    batch, batch_count = assignment_totals(
        recorded_section(text, "Historical batch results:"), BATCH,
    )
    tracking, size_count, threshold_count = tracking_totals(text)
    return [
        ("Single", f"{single_count} matrices", single),
        ("Batch", f"{batch_count} batches · automatic threads", batch),
        ("Tracking", f"{size_count} sizes × {threshold_count} thresholds", tracking),
    ]


def make_figure(panels):
    """Compare totals with horizontal bars on zero-based linear axes."""
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 15,
        "text.color": "#172b3a", "axes.labelcolor": "#4b5c6a",
        "xtick.color": "#4b5c6a", "ytick.color": "#172b3a",
        "svg.fonttype": "none", "svg.hashsalt": "lapx-benchmark-summary",
    })
    fig, axes = plt.subplots(1, 3, figsize=(16.8, 6.8))
    fig.subplots_adjust(left=.085, right=.975, top=.70, bottom=.13, wspace=.80)
    fig.patch.set_facecolor("white")
    fig.suptitle("LAPX BENCHMARK - TOTAL TIME (S)", x=.5, y=.96, fontsize=24, weight="bold")
    fig.text(.5, .885, "LAPX 0.13.0 · i9-13900KS · Windows 11 · Python 3.11.17",
             ha="center", fontsize=15, color="#4b5c6a")

    max_rows = max(len(totals) for _, _, totals in panels)
    for index, (ax, (title, subtitle, totals)) in enumerate(zip(axes, panels)):
        panel_left = .018 + index * .328
        panel_width = .308
        label_space = .13 if title == "Batch" else .072
        ax.set_position([panel_left + label_space, .13,
                         panel_width - label_space - .025, .57])
        fig.add_artist(Rectangle(
            (panel_left, .105), panel_width, .73, transform=fig.transFigure,
            fill=False, edgecolor="#cbd5de", linewidth=1.1,
        ))
        heading_x = (.018 - label_space) / (panel_width - label_space - .025)
        ordered = sorted(totals.items(), key=lambda item: item[1])
        ax.set_xlim(0, float(max(totals.values())) * 1.22)
        ax.set_ylim(max_rows - .5, -.5)
        ax.set_xticks([])
        ax.set_yticks(range(len(ordered)))
        ax.set_yticklabels([name for name, _ in ordered], fontsize=14)
        ax.tick_params(axis="both", length=0, pad=9)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_title(title, loc="left", x=heading_x, fontsize=20, weight="bold", pad=36)
        ax.text(heading_x, 1.035, subtitle, transform=ax.transAxes,
                fontsize=13, color="#4b5c6a")
        for y, (name, total) in enumerate(ordered):
            color = "#65788a"
            if name.startswith("lapjvr"):
                color = "#2875b9"
            elif name.startswith("lapjvh"):
                color = "#008576"
            elif name.startswith("SciPy"):
                color = "#303c46"
            ax.barh(y, float(total), height=.58, color=color, zorder=3)
            ax.annotate(f"{total:.3f}", (float(total), y),
                        xytext=(9, 0), textcoords="offset points", va="center",
                        fontsize=13, color=color)

    fig.text(.5, .055,
             "Sum of reported case times · lower is better · each panel has its own scale",
             ha="center", fontsize=15, color="#4b5c6a")
    output = ROOT / "docs"
    output.mkdir(exist_ok=True)
    fig.savefig(output / "benchmark_summary.png", dpi=160, facecolor="white",
                metadata={"Software": "LAPX benchmark summary"})
    fig.savefig(output / "benchmark_summary.svg", facecolor="white",
                metadata={"Date": None, "Creator": "LAPX benchmark summary"})
    svg_path = output / "benchmark_summary.svg"
    svg = svg_path.read_text(encoding="utf-8")
    svg_path.write_bytes(("\n".join(line.rstrip() for line in svg.splitlines()) + "\n").encode("utf-8"))
    plt.close(fig)


if __name__ == "__main__":
    panels = read_totals((ROOT / "benchmark.md").read_text(encoding="utf-8"))
    make_figure(panels)
    for title, _, totals in panels:
        print(title + " (seconds):")
        for name, total in sorted(totals.items(), key=lambda item: item[1]):
            print(f"  {name}: {total}")
