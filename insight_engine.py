import os
import pandas as pd
from matplotlib import pyplot as plt
from llm import generate_insights
from report_generator import create_pdf, create_ppt, create_zip
import datetime

os.makedirs("data", exist_ok=True)
os.makedirs("charts", exist_ok=True)
os.makedirs("output", exist_ok=True)


def read_and_concat(csv_paths):
    dfs = [pd.read_csv(p) for p in csv_paths]
    return pd.concat(dfs, ignore_index=True)


def clean_df(df):
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        df[col] = df[col].fillna(0)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def compute_metrics(df):
    metrics = {}
    metrics["total_rows"] = len(df)

    if "impressions" in df.columns and "clicks" in df.columns:
        imp = df["impressions"].sum()
        clk = df["clicks"].sum()
        metrics["impressions"] = int(imp)
        metrics["clicks"] = int(clk)
        metrics["ctr"] = round(clk / imp, 4) if imp > 0 else 0

    if "traffic" in df.columns and "city" in df.columns:
        top = df.groupby("city")["traffic"].sum().nlargest(5)
        metrics["top_cities"] = top.to_dict()

    return metrics


def generate_charts(df):
    chart_paths = []

    # Example CTR chart
    if "impressions" in df.columns and "clicks" in df.columns:
        plt.figure()
        df["ctr"] = df["clicks"] / df["impressions"].replace({0: 1})
        df["ctr"].plot(kind="line")
        plt.title("CTR Trend")
        f = f"charts/ctr_{datetime.datetime.now().timestamp()}.png"
        plt.savefig(f)
        plt.close()
        chart_paths.append(f)

    return chart_paths


def process_and_generate(csv_paths):
    df = read_and_concat(csv_paths)
    df = clean_df(df)

    metrics = compute_metrics(df)
    charts = generate_charts(df)

    prompt = f"""
    You are a data analyst. Produce an executive summary from these metrics:

    {metrics}

    Provide:
    - A 3–4 sentence executive summary
    - 3 bullet-point insights
    - 2 recommended actions
    """

    insights = generate_insights(prompt)

    pdf_path = create_pdf(metrics, charts, insights)
    ppt_path = create_ppt(metrics, charts, insights)
    zip_path = create_zip(pdf_path, ppt_path, charts)

    return zip_path
