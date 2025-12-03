import os
import pandas as pd
from utils_ingestion import load_file
from matplotlib import pyplot as plt
import seaborn as sns
from llm import generate_insights
from report_generator import create_pdf, create_ppt, create_zip
import datetime

sns.set_theme(style="whitegrid")

os.makedirs("charts", exist_ok=True)
os.makedirs("output", exist_ok=True)

def read_and_merge(files):
    dfs = []
    for f in files:
        try:
            dfs.append(load_file(f))
        except Exception as e:
            print(f"Failed to load {f}: {e}")
    return pd.concat(dfs, ignore_index=True)

def clean_df(df):
    df = df.dropna(how="all")

    # Convert date fields if present
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors="ignore")

    # Fill numeric nulls with 0
    df = df.fillna(0)

    return df

def compute_metrics(df):
    metrics = {}

    if "impressions" in df.columns and "clicks" in df.columns:
        imp = df["impressions"].sum()
        clk = df["clicks"].sum()
        metrics["CTR"] = round(clk / imp, 4) if imp > 0 else 0
        metrics["Total Impressions"] = int(imp)
        metrics["Total Clicks"] = int(clk)

    if "traffic" in df.columns and "city" in df.columns:
        metrics["Top Cities"] = df.groupby("city")["traffic"].sum().nlargest(5).to_dict()

    metrics["Row Count"] = len(df)
    return metrics

def generate_charts(df):
    chart_paths = []

    if "date" in df.columns and "impressions" in df.columns:
        df["ctr"] = df["clicks"] / df["impressions"].replace({0:1})
        df_sorted = df.sort_values("date")

        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df_sorted, x="date", y="ctr", marker="o")
        plt.title("CTR Trend Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        p = f"charts/ctr_{datetime.datetime.now().timestamp()}.png"
        plt.savefig(p, dpi=200)
        plt.close()
        chart_paths.append(p)

    if "city" in df.columns and "traffic" in df.columns:
        city_perf = df.groupby("city")["traffic"].sum().sort_values(ascending=False)
        plt.figure(figsize=(10, 5))
        sns.barplot(x=city_perf.index, y=city_perf.values)
        plt.title("Traffic by City")
        plt.tight_layout()
        p = f"charts/city_{datetime.datetime.now().timestamp()}.png"
        plt.savefig(p, dpi=200)
        plt.close()
        chart_paths.append(p)

    return chart_paths

def process_and_generate(files):
    df = read_and_merge(files)
    df = clean_df(df)

    metrics = compute_metrics(df)
    charts = generate_charts(df)

    prompt = f"""
    You are a senior data analyst. Summarize the dataset below in crisp executive language.
    Metrics: {metrics}
    Provide:
    - Executive summary
    - Key takeaways
    - Recommendations
    """
    insights = generate_insights(prompt)

    pdf = create_pdf(metrics, charts, insights)
    ppt = create_ppt(metrics, charts, insights)
    zip_path = create_zip(pdf, ppt, charts)

    return zip_path
