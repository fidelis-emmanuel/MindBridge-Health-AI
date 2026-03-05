import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "mentor.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cards = [
    # ── Tableau Basics ───────────────────────────────────────────────────────
    (
        "How do you connect Tableau Desktop to a live PostgreSQL database?",
        "In Tableau Desktop: Connect → To a Server → PostgreSQL. Enter server hostname, port (default 5432), database name, username, and password. Choose 'Live' connection to query in real time, or 'Extract' to pull data into a local .hyper file for offline analysis. For Railway PostgreSQL (as used in MindBridge), the host is the Railway-provided URL, port is the custom Railway port, and SSL must be enabled — set SSL Mode to 'require' in Tableau's connection dialog. Once connected, drag tables from the left panel onto the canvas to build the data source. You can join tables here before building visualizations.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the difference between a Tableau Dimension and a Measure?",
        "Dimensions are categorical/qualitative fields — they segment and group data. Examples: patient_name, risk_level, diagnosis. Tableau displays them in blue by default. Measures are quantitative fields — they are aggregated (summed, averaged, counted). Examples: medication_adherence, appointments_missed, crisis_calls_30days. Tableau displays them in green. When you drag risk_level to Rows and COUNT(patient_id) to Columns, Tableau builds a bar chart showing patient count per risk level. The distinction matters because dragging a dimension to a shelf filters/groups, while dragging a measure aggregates. Tableau infers type from the schema — strings become dimensions, numbers become measures — but you can right-click and convert if needed.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is a Tableau calculated field and when would you use one in healthcare data?",
        "A calculated field is a new column you define using Tableau's formula language, computed on the fly from existing fields. Create one: Analysis → Create Calculated Field. Example for MindBridge: [medication_adherence] * 100 to convert the 0–1 float to a percentage. Or: IF [risk_level] = 'CRITICAL' OR [risk_level] = 'HIGH' THEN 'Elevated' ELSE 'Stable' END to create a binary flag for a summary view. Or: IF [appointments_missed] >= 3 AND [medication_adherence] < 0.5 THEN 'Intervention Needed' ELSE 'Monitor' END to combine clinical signals into an action category. Calculated fields are useful when the database stores normalized values but the dashboard needs derived clinical indicators.",
        "CON", 0, 2.5, 1
    ),
    (
        "How do you build a Tableau dashboard from multiple worksheets?",
        "A Tableau workbook contains Sheets (individual charts) and Dashboards (compositions of sheets). To build a dashboard: New Dashboard → drag sheets from the left panel onto the canvas. Set the size (fixed px or automatic). Use Layout containers (horizontal/vertical) to organize charts. Add filters: right-click any sheet's filter and select 'Apply to Worksheets → All Using This Data Source' to make one filter control all charts simultaneously. Add interactivity: click a sheet's dropdown → Use as Filter — clicking a bar in one chart filters all other charts. For a patient risk dashboard: Sheet 1 = risk level bar chart, Sheet 2 = medication adherence scatter, Sheet 3 = patient count KPI tiles. Combine them on one dashboard with a shared risk_level filter.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the difference between Tableau's COUNTD and COUNT functions?",
        "COUNT counts all rows including duplicates. COUNTD (count distinct) counts unique values. For healthcare: COUNT([patient_id]) counts total appointment records. COUNTD([patient_id]) counts unique patients who had appointments — the correct denominator for 'how many patients are active'. If a patient has 5 appointments, COUNT adds 5, COUNTD adds 1. This distinction is critical in healthcare analytics: medication adherence rates should be computed per unique patient, not per encounter row. Use COUNTD when your data is at the event/transaction level but your metric is at the patient level.",
        "CON", 0, 2.5, 1
    ),

    # ── Pandas ───────────────────────────────────────────────────────────────
    (
        "How do you load a PostgreSQL query result into a Pandas DataFrame?",
        "Use SQLAlchemy or psycopg2 with pandas.read_sql(). Example:\n\nimport pandas as pd\nfrom sqlalchemy import create_engine\n\nengine = create_engine('postgresql://user:password@host:port/dbname')\ndf = pd.read_sql('SELECT * FROM patients', engine)\n\nFor Railway PostgreSQL, construct the URL from environment variables. The result is a DataFrame where each column maps to a database column and each row is a patient record. Alternatively, fetch rows manually and pass to pd.DataFrame(rows, columns=[col names]). Use pd.read_sql_query() when you want to pass a parameterized query. The DataFrame is in-memory — suitable for analysis on small-to-medium datasets, not for streaming millions of rows.",
        "CON", 0, 2.5, 1
    ),
    (
        "What are the most commonly used Pandas operations for healthcare data analysis?",
        "Core operations: df.describe() — summary statistics (mean, std, min, max, quartiles) for numeric columns like medication_adherence. df.groupby('risk_level')['medication_adherence'].mean() — average adherence per risk tier. df[df['risk_level'] == 'CRITICAL'] — filter to critical patients. df['adherence_pct'] = df['medication_adherence'] * 100 — add a derived column. df.sort_values('appointments_missed', ascending=False) — rank patients by missed appointments. df.isnull().sum() — identify missing data per column. df.value_counts('risk_level') — count patients per risk level. df.corr() — correlation matrix between numeric clinical variables. df.pivot_table(values='medication_adherence', index='risk_level', aggfunc='mean') — cross-tabulation for dashboard summaries.",
        "CON", 0, 2.5, 1
    ),
    (
        "How do you handle missing data in a Pandas healthcare DataFrame?",
        "First, identify missing data: df.isnull().sum() shows the count per column. df.isnull().mean() shows the proportion. Then choose a strategy based on clinical context: df.dropna() removes rows with any missing value — appropriate if missing data is rare and random. df['medication_adherence'].fillna(df['medication_adherence'].mean()) — impute with mean, appropriate for continuous variables with < 5% missing. df['risk_level'].fillna('UNKNOWN') — explicit unknown category for categorical fields. df.dropna(subset=['patient_name', 'diagnosis']) — only drop rows missing required fields. In healthcare, never silently drop or impute without documenting — missing vital signs or diagnoses may indicate data entry failures, not random missingness. Always log how many rows were affected.",
        "CON", 0, 2.5, 1
    ),
    (
        "How do you use Pandas to compute a patient risk score from multiple clinical variables?",
        "Define weights and combine normalized variables. Example:\n\n# Normalize each variable to 0-1 scale\ndf['miss_score'] = df['appointments_missed'] / df['appointments_missed'].max()\ndf['crisis_score'] = df['crisis_calls_30days'] / df['crisis_calls_30days'].max()\ndf['adherence_score'] = 1 - df['medication_adherence']  # invert: low adherence = high risk\n\n# Weighted composite score\ndf['risk_score'] = (\n    0.4 * df['miss_score'] +\n    0.4 * df['crisis_score'] +\n    0.2 * df['adherence_score']\n)\n\ndf.sort_values('risk_score', ascending=False).head(10)\n\nThis surfaces the 10 highest-risk patients regardless of their categorical risk_level label. Useful for validating or supplementing the clinician-assigned risk tier.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the difference between df.apply(), df.map(), and df.groupby().transform() in Pandas?",
        "df['col'].map(func) — applies a function element-by-element to a single Series. Use for simple value transformations: df['risk_level'].map({'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}). df.apply(func, axis=1) — applies a function row-by-row across the entire DataFrame. Use when you need multiple columns: df.apply(lambda row: row['appointments_missed'] * row['crisis_calls_30days'], axis=1). df.groupby('risk_level')['medication_adherence'].transform('mean') — applies a group-level aggregation but returns a Series aligned to the original index, so each row gets its group's mean. Use this to add a 'group mean' column without collapsing the DataFrame. Rule of thumb: map for lookup/replace, apply for multi-column row logic, transform for group statistics that stay row-aligned.",
        "CON", 0, 2.5, 1
    ),

    # ── Matplotlib ───────────────────────────────────────────────────────────
    (
        "How do you create a bar chart of patient counts by risk level using Matplotlib?",
        "import matplotlib.pyplot as plt\nimport pandas as pd\n\ncounts = df['risk_level'].value_counts().reindex(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])\ncolors = ['#7f1d1d', '#ef4444', '#eab308', '#22c55e']\n\nfig, ax = plt.subplots(figsize=(8, 5))\nax.bar(counts.index, counts.values, color=colors, edgecolor='white', linewidth=0.5)\nax.set_title('Patient Distribution by Risk Level', fontsize=14, fontweight='bold')\nax.set_xlabel('Risk Level')\nax.set_ylabel('Number of Patients')\nfor i, (label, val) in enumerate(zip(counts.index, counts.values)):\n    ax.text(i, val + 0.1, str(val), ha='center', fontsize=11)\nplt.tight_layout()\nplt.savefig('risk_distribution.png', dpi=150)\nplt.show()\n\nKey details: reindex() ensures consistent ordering. Annotating bars with text() adds value labels. tight_layout() prevents label clipping.",
        "CON", 0, 2.5, 1
    ),
    (
        "How do you create a scatter plot showing medication adherence vs. appointments missed, colored by risk level?",
        "import matplotlib.pyplot as plt\n\ncolor_map = {'CRITICAL': '#7f1d1d', 'HIGH': '#ef4444', 'MEDIUM': '#eab308', 'LOW': '#22c55e'}\ncolors = df['risk_level'].map(color_map)\n\nfig, ax = plt.subplots(figsize=(9, 6))\nscatter = ax.scatter(\n    df['medication_adherence'] * 100,\n    df['appointments_missed'],\n    c=colors,\n    alpha=0.7,\n    edgecolors='white',\n    linewidth=0.5,\n    s=80\n)\nax.set_xlabel('Medication Adherence (%)')\nax.set_ylabel('Appointments Missed')\nax.set_title('Clinical Risk Indicators by Patient', fontsize=13, fontweight='bold')\n\n# Manual legend\nfrom matplotlib.patches import Patch\nlegend_elements = [Patch(facecolor=v, label=k) for k, v in color_map.items()]\nax.legend(handles=legend_elements, title='Risk Level')\n\nplt.tight_layout()\nplt.show()\n\nThis chart reveals clustering: high-risk patients typically appear in the lower-left quadrant (low adherence, many missed appointments).",
        "CON", 0, 2.5, 1
    ),
    (
        "How do you use Matplotlib subplots to create a multi-panel clinical dashboard figure?",
        "fig, axes = plt.subplots(2, 2, figsize=(14, 10))\nfig.suptitle('MindBridge Patient Population Overview', fontsize=16, fontweight='bold')\n\n# Panel 1: Risk distribution bar chart\nax1 = axes[0, 0]\ncounts = df['risk_level'].value_counts().reindex(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])\nax1.bar(counts.index, counts.values, color=['#7f1d1d','#ef4444','#eab308','#22c55e'])\nax1.set_title('Patients by Risk Level')\n\n# Panel 2: Adherence histogram\nax2 = axes[0, 1]\nax2.hist(df['medication_adherence'] * 100, bins=10, color='#3b82f6', edgecolor='white')\nax2.set_title('Medication Adherence Distribution')\nax2.set_xlabel('Adherence (%)')\n\n# Panel 3: Scatter\nax3 = axes[1, 0]\nax3.scatter(df['medication_adherence'] * 100, df['appointments_missed'], alpha=0.6)\nax3.set_title('Adherence vs. Missed Appointments')\n\n# Panel 4: Crisis calls box plot\nax4 = axes[1, 1]\ngroups = [df[df['risk_level']==r]['crisis_calls_30days'].values for r in ['LOW','MEDIUM','HIGH','CRITICAL']]\nax4.boxplot(groups, labels=['LOW','MEDIUM','HIGH','CRITICAL'])\nax4.set_title('Crisis Calls by Risk Level')\n\nplt.tight_layout()\nplt.savefig('clinical_overview.png', dpi=150)\nplt.show()\n\naxes[row, col] indexing is zero-based. suptitle() adds a figure-level title above all panels.",
        "CON", 0, 2.5, 1
    ),
    (
        "What is the difference between plt.plot() and ax.plot(), and which should you use?",
        "plt.plot() uses the implicit 'current axes' — Matplotlib maintains a global state machine tracking the active figure and axes. It is convenient for quick one-off plots but breaks down with subplots or when passing axes between functions. ax.plot() is explicit object-oriented style — you hold a reference to the axes object and call methods on it directly. Always use ax.plot() in any non-trivial code:\n\nfig, ax = plt.subplots()\nax.plot(df['medication_adherence'])\nax.set_title('Adherence Over Time')\n\nThe explicit style is required when working with subplots (you need to target a specific panel), when embedding charts in functions or classes, and when using Seaborn's ax= parameter. Rule: use plt.plot() only for throwaway exploratory plots in a notebook. Use ax.plot() for anything you will save, share, or reuse.",
        "CON", 0, 2.5, 1
    ),
]

inserted = 0
skipped = 0

for card in cards:
    try:
        cursor.execute("""
            INSERT INTO cards (question, answer, card_type, repetitions, ease_factor, interval)
            VALUES (?, ?, ?, ?, ?, ?)
        """, card)
        inserted += 1
    except sqlite3.IntegrityError:
        skipped += 1

conn.commit()
conn.close()

print(f"[OK] Day 18 cards loaded: {inserted} inserted, {skipped} skipped")
print(f"[*]  Topics: Tableau (PostgreSQL connection, dimensions/measures, calculated fields,")
print(f"             dashboards, COUNTD), Pandas (read_sql, groupby, missing data,")
print(f"             apply/map/transform, risk scoring), Matplotlib (bar charts, scatter,")
print(f"             subplots, explicit axes style)")
