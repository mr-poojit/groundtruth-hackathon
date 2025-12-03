import pandas as pd
import sqlite3
import json
import zipfile
import io
import re

def load_file(path):
    """Auto-detect and load different file types into a pandas DataFrame."""

    if path.endswith(".csv"):
        return pd.read_csv(path)

    elif path.endswith(".xlsx"):
        return pd.read_excel(path)

    elif path.endswith(".json"):
        return pd.read_json(path)

    elif path.endswith(".txt"):
        return pd.read_csv(path, sep=None, engine="python")

    elif path.endswith(".db"):
        conn = sqlite3.connect(path)
        # Fetch all tables
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        frames = []
        for t in tables["name"]:
            try:
                frames.append(pd.read_sql(f"SELECT * FROM {t}", conn))
            except Exception:
                pass
        conn.close()
        return pd.concat(frames, ignore_index=True)

    elif path.endswith(".sql"):
        # Extract SELECT queries from SQL dump
        with open(path, "r", encoding="utf-8") as f:
            sql_text = f.read()

        # Pick first SELECT query found
        match = re.search(r"(SELECT[\s\S]+?;)", sql_text, re.IGNORECASE)
        if not match:
            raise Exception("No SELECT query found in SQL file.")

        query = match.group(1)

        # Temporary in-memory database
        conn = sqlite3.connect(":memory:")

        try:
            # Load all CREATE TABLE and INSERT statements
            statements = sql_text.split(";")
            for stmt in statements:
                s = stmt.strip()
                if s.lower().startswith(("create table", "insert into")):
                    conn.execute(s)
            df = pd.read_sql(query, conn)
        finally:
            conn.close()

        return df

    elif path.endswith(".zip"):
        frames = []
        with zipfile.ZipFile(path, "r") as z:
            for name in z.namelist():
                if name.endswith((".csv", ".xlsx", ".json")):
                    content = z.read(name)
                    if name.endswith(".csv"):
                        frames.append(pd.read_csv(io.BytesIO(content)))
                    elif name.endswith(".xlsx"):
                        frames.append(pd.read_excel(io.BytesIO(content)))
                    elif name.endswith(".json"):
                        frames.append(pd.read_json(io.BytesIO(content)))
        return pd.concat(frames, ignore_index=True)

    else:
        raise Exception(f"Unsupported file format: {path}")
