import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analytics import get_marks_data, get_section_summary, get_subject_summary
from config import Config


def _get_charts_folder():
    """Ensure the static charts directory exists and return its path."""
    folder = Config.STATIC_CHARTS_DIR
    os.makedirs(folder, exist_ok=True)
    return folder


def generate_subject_average_chart():
    """
    Generate a bar chart showing average marks obtained per subject.
    Dynamically scales the Y-axis according to actual subject maximum marks.
    """
    subject_summary = get_subject_summary()
    if not subject_summary:
        return None

    chart_folder = _get_charts_folder()
    chart_path = os.path.join(chart_folder, "subject_average.png")

    df = pd.DataFrame(subject_summary)
    df = df.sort_values(by="average_marks", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    try:
        bars = ax.bar(
            df["subject_name"],
            df["average_marks"],
            color="#1f77b4",
            edgecolor="#0f4c81",
            width=0.55,
            alpha=0.9,
            label="Subject Mean Score"
        )

        # Dynamic Y-axis scale based on maximum marks across evaluated subjects
        max_limit = float(df["max_marks"].max()) if "max_marks" in df.columns else 100.0
        max_limit = max(max_limit, float(df["average_marks"].max()))
        ax.set_ylim(0, max_limit * 1.15)

        # Annotate bars with score and maximum marks
        for bar, (_, row) in zip(bars, df.iterrows()):
            height = bar.get_height()
            max_m = row.get("max_marks", 100.0)
            ax.annotate(
                f"{height:.1f} / {max_m:.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9.5,
                fontweight="bold",
            )

        # Draw average passing benchmark across subjects if available
        if "pass_marks" in df.columns and not df.empty:
            avg_pass_benchmark = float(df["pass_marks"].mean())
            ax.axhline(
                y=avg_pass_benchmark,
                color="#d62728",
                linestyle="--",
                linewidth=1.5,
                label=f"Passing Benchmark (~{avg_pass_benchmark:.0f} marks)",
            )

        ax.set_title("Subject-Wise Average Academic Performance", fontsize=13, fontweight="bold", pad=14)
        ax.set_xlabel("Curriculum Subject", fontsize=11, labelpad=8)
        ax.set_ylabel("Average Marks Obtained", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", framealpha=0.9)
        plt.xticks(rotation=20, ha="right", fontsize=9.5)
        plt.tight_layout()

        plt.savefig(chart_path, dpi=160)
        return "charts/subject_average.png"
    finally:
        plt.close(fig)


def generate_pass_fail_chart():
    """
    Generate a styled donut chart showing overall student clearance vs failure.
    Uses student-level status rather than isolated assessment counts.
    """
    df = get_marks_data()
    if df.empty:
        return None

    chart_folder = _get_charts_folder()
    chart_path = os.path.join(chart_folder, "pass_fail.png")

    fig, ax = plt.subplots(figsize=(7, 6))
    try:
        # Group by student to assess cumulative pass/fail
        student_results = []
        for _, s_df in df.groupby("student_id"):
            valid = s_df.dropna(subset=["mark_id"])
            if valid.empty:
                continue

            # Check if any subject average was below passing threshold
            failed = False
            for _, sub_df in valid.groupby("subject_id"):
                sub_score = sub_df["marks_obtained"].mean()
                sub_pass = sub_df["pass_marks"].iloc[0]
                if sub_score < sub_pass:
                    failed = True
                    break

            student_results.append("Fail" if failed else "Pass")

        if not student_results:
            return None

        pass_count = student_results.count("Pass")
        fail_count = student_results.count("Fail")

        counts = [pass_count, fail_count]
        labels = [f"Passed ({pass_count})", f"Failed ({fail_count})"]
        colors = ["#2ca02c", "#d62728"]

        filtered_data = [
            (c, l, col) for c, l, col in zip(counts, labels, colors) if c > 0
        ]
        if not filtered_data:
            return None

        counts, labels, colors = zip(*filtered_data)

        wedges, texts, autotexts = ax.pie(
            counts,
            labels=labels,
            autopct="%1.1f%%",
            startangle=140,
            colors=colors,
            wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
            pctdistance=0.75,
            textprops=dict(fontsize=11),
        )

        for at in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")
            at.set_fontsize(12)

        ax.set_title("Overall Student Clearance vs. Failure Ratio", fontsize=13, fontweight="bold", pad=12)
        plt.tight_layout()

        plt.savefig(chart_path, dpi=160)
        return "charts/pass_fail.png"
    finally:
        plt.close(fig)


def generate_marks_distribution_chart():
    """
    Generate a histogram showing the distribution of marks across assessments,
    with mean and median statistical reference lines.
    """
    df = get_marks_data()
    if df.empty or "marks_obtained" not in df.columns:
        return None

    marks = df["marks_obtained"].dropna().to_numpy(dtype=float)
    if marks.size == 0:
        return None

    chart_folder = _get_charts_folder()
    chart_path = os.path.join(chart_folder, "marks_distribution.png")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    try:
        # Dynamic upper bound for histogram range
        max_val = float(np.max(marks))
        upper_range = max(100.0, float(np.ceil(max_val / 10) * 10))

        counts, bins, patches = ax.hist(
            marks,
            bins=10,
            range=(0, upper_range),
            color="#4a90e2",
            edgecolor="#1a4c8a",
            alpha=0.85,
        )

        mean_val = float(np.mean(marks))
        median_val = float(np.median(marks))

        ax.axvline(
            mean_val,
            color="#e67e22",
            linestyle="-",
            linewidth=2,
            label=f"Mean: {mean_val:.1f} Marks",
        )
        ax.axvline(
            median_val,
            color="#27ae60",
            linestyle="--",
            linewidth=2,
            label=f"Median: {median_val:.1f} Marks",
        )

        ax.set_title("Assessment Marks Frequency Distribution", fontsize=13, fontweight="bold", pad=14)
        ax.set_xlabel("Marks Range", fontsize=11, labelpad=8)
        ax.set_ylabel("Frequency (Assessment Count)", fontsize=11, labelpad=8)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", framealpha=0.9)
        plt.tight_layout()

        plt.savefig(chart_path, dpi=160)
        return "charts/marks_distribution.png"
    finally:
        plt.close(fig)


def generate_subject_pass_rate_chart():
    """
    Generate a bar chart showing pass percentages across curriculum subjects.
    """
    subject_summary = get_subject_summary()
    if not subject_summary:
        return None

    chart_folder = _get_charts_folder()
    chart_path = os.path.join(chart_folder, "subject_pass_rate.png")

    df = pd.DataFrame(subject_summary)
    df = df.sort_values(by="pass_percentage", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    try:
        bars = ax.bar(
            df["subject_name"],
            df["pass_percentage"],
            color="#17a2b8",
            edgecolor="#117a8b",
            width=0.55,
            alpha=0.9,
        )

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_title("Subject-Wise Examination Pass Percentages", fontsize=13, fontweight="bold", pad=14)
        ax.set_xlabel("Curriculum Subject", fontsize=11, labelpad=8)
        ax.set_ylabel("Pass Rate (%)", fontsize=11, labelpad=8)
        ax.set_ylim(0, 115)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        plt.xticks(rotation=20, ha="right", fontsize=9.5)
        plt.tight_layout()

        plt.savefig(chart_path, dpi=160)
        return "charts/subject_pass_rate.png"
    finally:
        plt.close(fig)


def generate_section_performance_chart():
    """
    Generate a bar chart comparing cohort performance across class sections.
    Uses normalized average percentage for a fair comparison.
    """
    section_summary = get_section_summary()
    if not section_summary:
        return None

    chart_folder = _get_charts_folder()
    chart_path = os.path.join(chart_folder, "section_performance.png")

    df = pd.DataFrame(section_summary)

    fig, ax = plt.subplots(figsize=(8, 5))
    try:
        palette = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6"]
        colors = [palette[i % len(palette)] for i in range(len(df))]

        # Use average percentage if available, otherwise average marks
        metric_col = "average_percentage" if "average_percentage" in df.columns else "average_marks"
        metric_label = "Average Percentage (%)" if metric_col == "average_percentage" else "Average Marks"

        bars = ax.bar(
            [f"Section {s}" for s in df["section"]],
            df[metric_col],
            color=colors,
            edgecolor="#333333",
            width=0.5,
            alpha=0.9,
        )

        for bar in bars:
            height = bar.get_height()
            suffix = "%" if metric_col == "average_percentage" else ""
            ax.annotate(
                f"{height:.1f}{suffix}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_title("Class Section Academic Performance Comparison", fontsize=13, fontweight="bold", pad=14)
        ax.set_xlabel("Academic Cohort / Section", fontsize=11, labelpad=8)
        ax.set_ylabel(metric_label, fontsize=11, labelpad=8)
        ax.set_ylim(0, 115)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        plt.tight_layout()

        plt.savefig(chart_path, dpi=160)
        return "charts/section_performance.png"
    finally:
        plt.close(fig)


def generate_all_charts():
    """
    Generate all five core analytical charts and return relative URL mapping.
    Safely captures errors to prevent crashing web request lifecycle.
    """
    return {
        "subject_average": generate_subject_average_chart(),
        "pass_fail": generate_pass_fail_chart(),
        "marks_distribution": generate_marks_distribution_chart(),
        "subject_pass_rate": generate_subject_pass_rate_chart(),
        "section_performance": generate_section_performance_chart(),
    }
