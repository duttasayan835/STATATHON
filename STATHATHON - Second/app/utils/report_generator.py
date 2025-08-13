from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import pandas as pd


def normalize_text_to_list(text):
    if not text:
        return []
    # If text is already a list, return it after cleaning
    if isinstance(text, list):
        return [line.strip() for line in text if line and line.strip()]
    # If text is a string, split by newlines and strip empty entries
    return [line.strip() for line in text.split("\n") if line.strip()]

def generate_report(stats, charts, output_pdf_path, executive_summary, cleaning_notes, recommendations, introduction="", methods="", conclusion=""):
    env = Environment(loader=FileSystemLoader("app/templates"))
    template = env.get_template("report_template.html")
    executive_summary_list = normalize_text_to_list(executive_summary)
    recommendations_list = normalize_text_to_list(recommendations)
    cleaning_notes_list = normalize_text_to_list(cleaning_notes)
    introduction_list = normalize_text_to_list(introduction)
    methods_list = normalize_text_to_list(methods)
    conclusion_list = normalize_text_to_list(conclusion)
    html_content = template.render(
        title="Dataset Analysis Report",
        dataset_name="Uploaded Dataset",
        date=pd.Timestamp.now().strftime("%B %d, %Y"),
        stats=stats,
        charts=charts,
        executive_summary=executive_summary_list,
        cleaning_notes=cleaning_notes_list,
        recommendations=recommendations_list,
        introduction=introduction_list,
        methods=methods_list,
        conclusion=conclusion_list
    )

    HTML(string=html_content).write_pdf(output_pdf_path)
    return output_pdf_path