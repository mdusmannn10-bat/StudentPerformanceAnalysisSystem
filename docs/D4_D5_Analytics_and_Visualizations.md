# D4 & D5. Data Analysis Methodology & Visualizations

## 1. Data Analysis Overview
The analytical core of the **Student Performance Analysis System** is decoupled from web presentation inside [`analytics.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/analytics.py), combining **Pandas** for structured multi-table aggregations and **NumPy** for descriptive statistical calculations.

---

## 2. Three-Tier Evaluation Model & Mathematical Formulas

The system implements a transparent 3-tier hierarchy that distinguishes granular assessment iterations from course mastery and cumulative student standing:

### Tier 1: Granular Assessment Level
For student $i$, curriculum subject $s$, and assessment iteration $a$ (e.g., *Internal 1*, *Internal 2*):
- $\text{Score Obtained}: m_{i,s,a}$
- Permitted Range: $0 \le m_{i,s,a} \le \text{MaxMarks}_s$
- Assessment Clearance:
  $$\text{Assessment Status}_{i,s,a} = \begin{cases} \text{Pass} & \text{if } m_{i,s,a} \ge \text{PassMarks}_s \\ \text{Fail} & \text{if } m_{i,s,a} < \text{PassMarks}_s \end{cases}$$

### Tier 2: Subject Level (Course Mastery)
When multiple assessments are recorded for a single subject, the system avoids inflating total marks by applying an assessment aggregation policy ($\text{AVERAGE}$ by default):
$$\bar{m}_{i,s} = \frac{1}{K_{i,s}} \sum_{a=1}^{K_{i,s}} m_{i,s,a}$$
$$\text{Subject Percentage}_{i,s} = \left( \frac{\bar{m}_{i,s}}{\text{MaxMarks}_s} \right) \times 100$$
$$\text{Subject Status}_{i,s} = \begin{cases} \text{Pass} & \text{if } \bar{m}_{i,s} \ge \text{PassMarks}_s \\ \text{Fail} & \text{if } \bar{m}_{i,s} < \text{PassMarks}_s \end{cases}$$
*Crucial Principle:* An individual failed assessment does not automatically fail the student in the subject if their subject aggregate average clears the passing benchmark.

### Tier 3: Cumulative Student Overall Standing
Let $S_i$ represent the set of distinct curriculum subjects attempted by student $i$:
$$\text{Total Marks Obtained}_i = \sum_{s \in S_i} \bar{m}_{i,s}$$
$$\text{Total Maximum Marks}_i = \sum_{s \in S_i} \text{MaxMarks}_s$$
$$\text{Overall Percentage}_i = \left( \frac{\text{Total Marks Obtained}_i}{\text{Total Maximum Marks}_i} \right) \times 100$$
$$\text{Backlog Count}_i = |\{s \in S_i : \bar{m}_{i,s} < \text{PassMarks}_s\}|$$

$$\text{Overall Status}_i = \begin{cases} 
\text{"No Marks Yet"} & \text{if } |S_i| = 0 \\
\text{"Fail"} & \text{if } \text{Backlog Count}_i > 0 \\
\text{"Pass"} & \text{if } \text{Backlog Count}_i = 0 \text{ and } |S_i| > 0
\end{cases}$$

### Letter Grading Scale:
$$\text{Grade}_i = \begin{cases} 
\text{F} & \text{if Backlog Count}_i > 0 \\
\text{A+} & \text{if } \text{Overall Percentage}_i \ge 90.0\% \\
\text{A} & \text{if } 80.0\% \le \text{Overall Percentage}_i < 90.0\% \\
\text{B} & \text{if } 70.0\% \le \text{Overall Percentage}_i < 80.0\% \\
\text{C} & \text{if } 60.0\% \le \text{Overall Percentage}_i < 70.0\% \\
\text{D} & \text{if } 50.0\% \le \text{Overall Percentage}_i < 60.0\% \\
\text{E} & \text{if } 35.0\% \le \text{Overall Percentage}_i < 50.0\% \\
\text{F} & \text{if } \text{Overall Percentage}_i < 35.0\%
\end{cases}$$

---

## 3. NumPy Descriptive Statistics
Executed by `get_marks_summary()` across all valid assessment scores ($N$ records):
- **Mean ($\mu$):** $\mu = \frac{1}{N} \sum_{j=1}^N x_j$
- **Median ($\tilde{x}$):** Middle value of the sorted marks vector.
- **Sample Standard Deviation ($\sigma$):** $\sigma = \sqrt{\frac{1}{N} \sum_{j=1}^N (x_j - \mu)^2}$
- **Variance ($\sigma^2$):** $\sigma^2 = \frac{1}{N} \sum_{j=1}^N (x_j - \mu)^2$
- **Interquartile Range (IQR):**
  - First Quartile ($Q_1$): 25th percentile
  - Third Quartile ($Q_3$): 75th percentile
  - $\text{IQR} = Q_3 - Q_1$

---

## 4. Pandas Aggregation Summaries
1. **Subject Summary (`get_subject_summary`):**
   - Groups marks DataFrame by `[subject_id, subject_name]`.
   - Aggregates assessment count, mean score, highest score, lowest score, and pass count.
   - Computes subject pass percentage:
     $$\text{Subject Pass Rate} = \left(\frac{\text{Passed Assessments}}{\text{Total Assessments}}\right) \times 100$$

2. **Cohort / Section Summary (`get_section_summary`):**
   - Groups marks DataFrame by `section` (e.g. A, B, C).
   - Aggregates student headcount, total assessment entries, mean marks, normalized average percentage, and cohort pass rate.

3. **At-Risk Diagnostic Model (`get_students_needing_support`):**
   - Evaluates each student against a configurable threshold $\theta$ (default: $40.0\%$).
   - Flags student if $\text{Overall Percentage} < \theta$ OR $\text{Backlog Count} \ge 1$.
   - Generates actionable remedial advice (e.g., *Remedial classes needed in Python Programming*).

---

## 5. Visualizations & Chart Catalog

All visualizations are produced by [`charts.py`](file:///c:/Users/Mohammad%20Usman/Documents/StudentPerformanceAnalysisSystem/charts.py) using **Matplotlib** with the non-blocking `Agg` backend:

### Chart 1: Subject-Wise Average Academic Performance
- **File:** `static/charts/subject_average.png`
- **Chart Type:** Vertical Bar Chart with dynamic Y-axis scaling.
- **X-Axis:** Curriculum Subject
- **Y-Axis:** Average Marks Obtained (auto-scaled to subject maximums)
- **Visual Features:** Direct numerical score annotations atop bars (`score / max`); passing benchmark line.
- **Interpretation:** Enables department chairs to detect courses where average student performance lags or excels.

### Chart 2: Overall Student Clearance vs. Failure Ratio
- **File:** `static/charts/pass_fail.png`
- **Chart Type:** Styled Donut / Pie Chart based on cumulative student clearance.
- **Slices:** Green (Passed) vs. Red (Failed)
- **Visual Features:** Percentage callouts, absolute headcount per category, 45% inner hole radius.
- **Interpretation:** Gives academic administrators an instantaneous visual summary of semester clearance.

### Chart 3: Assessment Marks Frequency Distribution
- **File:** `static/charts/marks_distribution.png`
- **Chart Type:** 10-Bin Histogram with dynamic upper range.
- **X-Axis:** Marks Range
- **Y-Axis:** Frequency (Assessment Count)
- **Visual Features:** Vertical solid line for Mean score ($\mu$); vertical dashed line for Median ($\tilde{x}$).
- **Interpretation:** Displays score skewness, clustering, and normal or bimodal tendencies across assessments.

### Chart 4: Subject-Wise Examination Pass Percentages
- **File:** `static/charts/subject_pass_rate.png`
- **Chart Type:** Bar Chart
- **X-Axis:** Curriculum Subject
- **Y-Axis:** Pass Rate (%) (Scale 0% to 115%)
- **Visual Features:** Teal bars with percentage labels.
- **Interpretation:** Identifies subjects with high failure rates that require curricular or pedagogical review.

### Chart 5: Class Section Academic Performance Comparison
- **File:** `static/charts/section_performance.png`
- **Chart Type:** Multi-color Section Comparison Bar Chart
- **X-Axis:** Class Section (A, B, C)
- **Y-Axis:** Average Percentage (%)
- **Visual Features:** Color-coded bars for each cohort with percentage annotations.
- **Interpretation:** Identifies inter-section performance disparity between student cohorts.
