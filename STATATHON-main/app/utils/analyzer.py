import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from statsmodels.stats.weightstats import DescrStatsW

plt.switch_backend('Agg')  # For headless environments

def compute_weighted_stats(df, weight_col=None):
    results = []
    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        if col == weight_col:
            continue
        if weight_col and weight_col in df.columns:
            dsw = DescrStatsW(df[col], weights=df[weight_col], ddof=0)
            mean = dsw.mean
            se = dsw.std_mean
        else:
            mean = df[col].mean()
            se = df[col].std() / (len(df[col]) ** 0.5)

        moe = 1.96 * se
        results.append({
            "variable": col,
            "mean": round(mean, 2),
            "se": round(se, 2),
            "moe": round(moe, 2)
        })

    return results

def generate_chart(df, col, chart_path):
    plt.figure(figsize=(6, 4))
    if df[col].dtype == 'object':
        sns.countplot(y=df[col], color='skyblue')
    else:
        sns.histplot(df[col], kde=True, color='coral')
    plt.title(f"Distribution of {col}")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

def generate_chart_caption(df, col):
    if df[col].dtype != 'object':
        return f"The average {col} is {df[col].mean():.2f} with a spread of {df[col].std():.2f}."
    else:
        top_cat = df[col].value_counts().idxmax()
        top_pct = df[col].value_counts(normalize=True).max() * 100
        return f"The most frequent category in {col} is '{top_cat}' ({top_pct:.1f}%)."

def plot_to_base64(col, df):
    buf = BytesIO()
    plt.figure(figsize=(6, 4))
    if df[col].dtype == 'object':
        sns.countplot(y=df[col], color='skyblue')
    else:
        sns.histplot(df[col], kde=True, color='coral')
    plt.title(f"Distribution of {col}")
    plt.tight_layout()
    plt.savefig(buf, format='png', bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def correlation_heatmap(df):
    numeric_df = df.select_dtypes(include=['number'])
    if numeric_df.shape[1] < 2:
        return None
    plt.figure(figsize=(8, 6))
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap="viridis", fmt=".2f")  # changed cmap
    plt.title("Correlation Heatmap")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def boxplot_column(df, col):
    plt.figure(figsize=(6, 4))
    sns.boxplot(x=df[col], color='lightgreen')
    plt.title(f"Boxplot for {col}")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def pie_chart(df, col):
    plt.figure(figsize=(6, 6))
    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0']  # Example palette
    df[col].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=colors)
    plt.ylabel('')
    plt.title(f"Pie Chart of {col}")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def scatter_plot(df, col1, col2):
    plt.figure(figsize=(6, 6))
    sns.scatterplot(x=col1, y=col2, data=df, color='purple')
    plt.title(f"Scatter Plot of {col1} vs {col2}")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()
