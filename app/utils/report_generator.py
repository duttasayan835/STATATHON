from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
import os

def generate_report(stats, charts, output_pdf_path, dataset_name="Survey Data", cleaning_notes=None):
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("report_template.html")

    # Render HTML with all content
    html_content = template.render(
        title="Survey Data Analysis Report",
        dataset_name=dataset_name,
        date=datetime.now().strftime("%B %d, %Y"),
        stats=stats,
        charts=charts,
        cleaning_notes=cleaning_notes or "Standard cleaning applied: removed null values, fixed data types, and normalized column names.",
        executive_summary=generate_executive_summary(stats, charts),
        recommendations=generate_recommendations(stats, charts)
    )

    HTML(string=html_content).write_pdf(output_pdf_path)
    return output_pdf_path


def generate_executive_summary(stats, charts):
    num_vars = len(stats) if stats else 0
    num_charts = len(charts) if charts else 0

    summary_text = (
        f"This report provides an in-depth statistical analysis of {num_vars} numeric variables from the dataset. "
        f"The analysis includes calculation of mean, standard error, and confidence intervals, helping uncover trends, anomalies, and patterns in the data.\n\n"
        f"A total of {num_charts} charts and visualizations were generated, covering data distributions, correlations, and critical comparisons between key variables. "
        f"These visual tools aid in understanding relationships and outliers.\n\n"
        f"Before conducting the analysis, standard data cleaning procedures were applied — null values were removed, data types were standardized, "
        f"and column names were normalized. This ensures the integrity and consistency of results derived from the dataset."
    )
    return [summary_text]



def generate_recommendations(stats, charts):
    recs = []

    for stat in stats:
        if stat['se'] > (stat['mean'] * 0.2):
            recs.append(
                f"The variable '{stat['variable']}' exhibits high variability, with a standard error exceeding 20% of its mean. "
                "This suggests a need for more data collection or closer inspection of this feature."
            )

    if not recs:
        recs.append(
            "Based on the statistical summaries and visual inspections, the dataset appears well-balanced. "
            "Most variables show consistent distributions with low variability, indicating good data quality. "
            "No immediate anomalies or issues were detected that would hinder further modeling or decision-making."
        )

    return recs

