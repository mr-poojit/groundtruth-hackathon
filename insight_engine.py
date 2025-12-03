# insight_engine.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from sklearn.ensemble import IsolationForest

from utils_ingestion import load_file
from report_generator import create_pdf, create_ppt, create_zip
from llm import generate_insights

sns.set_theme(style="whitegrid")

os.makedirs("charts", exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("data", exist_ok=True)


# ------------------------------------------------------
# INGESTION
# ------------------------------------------------------
def read_and_merge(paths):
    frames = []
    for p in paths:
        try:
            df = load_file(p)
            frames.append(df)
        except Exception as e:
            print(f"[ERROR] Failed to load {p}: {e}")

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)


# ------------------------------------------------------
# CLEANING
# ------------------------------------------------------
def clean_df(df):
    df = df.dropna(how="all").copy()
    df.columns = [c.strip() for c in df.columns]

    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except:
                pass

    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="ignore")
            except:
                pass

    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(0)

    if "city" in df.columns:
        df["city"] = df["city"].astype(str)

    return df


# ------------------------------------------------------
# METRICS
# ------------------------------------------------------
def compute_metrics(df):
    metrics = {"Row Count": int(len(df))}

    if {"impressions", "clicks"}.issubset(df.columns):
        imp = int(df["impressions"].sum())
        clk = int(df["clicks"].sum())
        metrics["Total Impressions"] = imp
        metrics["Total Clicks"] = clk
        metrics["CTR"] = round((clk / imp) if imp > 0 else 0, 4)

    if {"city", "traffic"}.issubset(df.columns):
        top = df.groupby("city")["traffic"].sum().nlargest(5)
        metrics["Top Cities"] = top.to_dict()

    return metrics


# ------------------------------------------------------
# ANOMALY DETECTION
# ------------------------------------------------------
def detect_anomalies(df):
    anomalies = []

    # --- 1) Traffic spikes/drops ---
    if {"date", "city", "traffic"}.issubset(df.columns):
        tmp = df[["date", "city", "traffic"]].copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"]).sort_values(["city", "date"])

        tmp["prev"] = tmp.groupby("city")["traffic"].shift(1)
        tmp["pct_change"] = (tmp["traffic"] - tmp["prev"]) / tmp["prev"]
        tmp = tmp.dropna(subset=["pct_change"])

        for _, r in tmp.iterrows():
            if r["pct_change"] <= -0.35:
                anomalies.append(
                    f"Traffic dropped {abs(r['pct_change']) * 100:.1f}% in {r['city']} on {r['date'].date()}"
                )
            elif r["pct_change"] >= 0.50:
                anomalies.append(
                    f"Traffic spiked {r['pct_change'] * 100:.1f}% in {r['city']} on {r['date'].date()}"
                )

    # --- 2) CTR changes ---
    if {"impressions", "clicks", "date"}.issubset(df.columns):
        tmp = df.copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.sort_values("date")

        tmp["ctr"] = tmp["clicks"] / tmp["impressions"].replace({0: None})
        tmp["ctr_prev"] = tmp["ctr"].shift(1)
        tmp = tmp.dropna(subset=["ctr", "ctr_prev"])

        tmp["ctr_change"] = (tmp["ctr"] - tmp["ctr_prev"]) / tmp["ctr_prev"]

        for _, r in tmp.iterrows():
            if r["ctr_change"] <= -0.40:
                anomalies.append(f"CTR dropped {abs(r['ctr_change']) * 100:.1f}% on {r['date'].date()}")
            elif r["ctr_change"] >= 0.40:
                anomalies.append(f"CTR increased {r['ctr_change'] * 100:.1f}% on {r['date'].date()}")

    # --- 3) IsolationForest Outliers ---
    if {"impressions", "clicks", "traffic"}.issubset(df.columns):
        subset = df[["impressions", "clicks", "traffic"]].fillna(0)

        if len(subset) >= 20:
            try:
                iso = IsolationForest(contamination=0.02, random_state=42)
                preds = iso.fit_predict(subset)
                outliers = df.iloc[(preds == -1).nonzero()[0]]

                for _, r in outliers.iterrows():
                    anomalies.append(
                        f"Outlier detected in {r.get('city', 'unknown')} on {r.get('date', '')} "
                        f"(impressions={int(r['impressions'])}, clicks={int(r['clicks'])}, traffic={int(r['traffic'])})"
                    )
            except Exception as e:
                print("[IsolationForest Error]", e)

    if not anomalies:
        anomalies.append("No significant anomalies detected.")

    return anomalies


# ------------------------------------------------------
# CHART GENERATION (fixed datetime issue)
# ------------------------------------------------------
def generate_charts(df, base_name):
    chart_files = []
    ts = int(datetime.datetime.now().timestamp())

    # --- CTR trend ---
    if {"date", "impressions", "clicks"}.issubset(df.columns):
        tmp = df.copy()
        tmp["date"] = pd.to_datetime(tmp["date"], errors="coerce")
        tmp = tmp.dropna(subset=["date"])

        numeric_cols = tmp.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            daily = tmp.groupby(tmp["date"].dt.date)[numeric_cols].sum()
        else:
            daily = pd.DataFrame()

        if not daily.empty:
            daily["ctr"] = daily["clicks"] / daily["impressions"].replace({0: None})

            plt.figure(figsize=(10, 4.5))
            sns.lineplot(x=daily.index, y=daily["ctr"], marker="o")
            plt.title("CTR Over Time")
            plt.xticks(rotation=45)
            plt.tight_layout()

            p = f"charts/{base_name}_ctr_{ts}.png"
            plt.savefig(p, dpi=200)
            plt.close()
            chart_files.append(p)

    # --- Traffic by city ---
    if {"city", "traffic"}.issubset(df.columns):
        city_sum = df.groupby("city")["traffic"].sum().sort_values(ascending=False)

        plt.figure(figsize=(10, 4))
        sns.barplot(x=city_sum.index, y=city_sum.values, palette="muted")
        plt.title("Traffic by City")
        plt.xticks(rotation=45)
        plt.tight_layout()

        p = f"charts/{base_name}_city_{ts}.png"
        plt.savefig(p, dpi=200)
        plt.close()
        chart_files.append(p)

    # --- Impressions distribution ---
    if "impressions" in df.columns:
        plt.figure(figsize=(8, 4))
        sns.boxplot(x=df["impressions"])
        plt.title("Impressions Distribution")
        plt.tight_layout()

        p = f"charts/{base_name}_impr_box_{ts}.png"
        plt.savefig(p, dpi=200)
        plt.close()
        chart_files.append(p)

    return chart_files


# ------------------------------------------------------
# ORCHESTRATION (FINAL VERSION WITH ANOMALY LIMITER)
# ------------------------------------------------------
def process_and_generate(paths, base_name):
    df = read_and_merge(paths)
    if df.empty:
        raise ValueError("No data loaded from files.")

    df = clean_df(df)
    metrics = compute_metrics(df)

    anomalies = detect_anomalies(df)

    # ----------------------------
    # LIMIT ANOMALIES FOR REPORTING
    # ----------------------------
    MAX_ANOMALIES = 5
    if len(anomalies) > MAX_ANOMALIES:
        extra = len(anomalies) - MAX_ANOMALIES
        anomalies = anomalies[:MAX_ANOMALIES]
        anomalies.append(f"... plus {extra} more anomalies (summarized).")

    charts = generate_charts(df, base_name)

    prompt = (
        "You are a senior data analyst. Provide:\n"
        "- A short executive summary (3–4 sentences)\n"
        "- Three bullet takeaways\n"
        "- Three action recommendations\n"
        f"Metrics: {metrics}\n"
        f"Anomalies: {anomalies}\n"
    )

    insights = generate_insights(prompt)

    pdf_path = create_pdf(metrics, charts, insights, base_name, anomalies)
    ppt_path = create_ppt(metrics, charts, insights, base_name, anomalies)
    zip_path = create_zip(pdf_path, ppt_path, charts, base_name)

    return zip_path
