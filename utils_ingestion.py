# utils_ingestion.py
import pandas as pd
import sqlite3
import io
import zipfile
import re
import os

def _read_csv_bytes(content_bytes):
    return pd.read_csv(io.BytesIO(content_bytes))

def _read_excel_bytes(content_bytes):
    return pd.read_excel(io.BytesIO(content_bytes))

def _read_json_bytes(content_bytes):
    return pd.read_json(io.BytesIO(content_bytes))

def load_file(path):
    """
    Auto-detect and load a file on disk into a pandas.DataFrame.
    Supported: .csv, .xlsx, .json, .txt (delimited), .db (sqlite), .sql (simple),
               .zip (containing csv/xlsx/json).
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} does not exist")

    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path)

    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(path)

    if lower.endswith(".json"):
        return pd.read_json(path)

    if lower.endswith(".txt"):
        # attempt to read as CSV with automatic delimiter sniff
        try:
            return pd.read_csv(path, sep=None, engine="python")
        except Exception:
            # fallback to plain read
            return pd.read_csv(path)

    if lower.endswith(".db") or lower.endswith(".sqlite"):
        conn = sqlite3.connect(path)
        try:
            tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
            frames = []
            for t in tables["name"].tolist():
                try:
                    frames.append(pd.read_sql(f"SELECT * FROM `{t}`", conn))
                except Exception:
                    # ignore problematic tables
                    pass
            if not frames:
                return pd.DataFrame()
            return pd.concat(frames, ignore_index=True, sort=False)
        finally:
            conn.close()

    if lower.endswith(".sql"):
        # Very simple parser: load all CREATE/INSERT then run first SELECT query
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            sql_text = f.read()

        # find SELECT ... ; block
        match = re.search(r"(SELECT[\s\S]+?;)", sql_text, re.IGNORECASE)
        # If no select, try to load insert statements into memory DB and select * from first table
        conn = sqlite3.connect(":memory:")
        try:
            statements = re.split(r";\s*\n", sql_text)
            for stmt in statements:
                s = stmt.strip()
                if not s:
                    continue
                try:
                    conn.execute(s)
                except Exception:
                    # ignore statements we cannot run
                    pass

            if match:
                q = match.group(1)
                q = q.rstrip(";")
                return pd.read_sql(q, conn)
            else:
                # fallback: list tables and return first
                tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
                if not tables.empty:
                    first = tables['name'].iloc[0]
                    return pd.read_sql(f"SELECT * FROM `{first}`", conn)
                return pd.DataFrame()
        finally:
            conn.close()

    if lower.endswith(".zip"):
        frames = []
        with zipfile.ZipFile(path, "r") as z:
            for name in z.namelist():
                if name.lower().endswith(".csv"):
                    try:
                        frames.append(pd.read_csv(io.BytesIO(z.read(name))))
                    except Exception:
                        pass
                elif name.lower().endswith((".xlsx", ".xls")):
                    try:
                        frames.append(pd.read_excel(io.BytesIO(z.read(name))))
                    except Exception:
                        pass
                elif name.lower().endswith(".json"):
                    try:
                        frames.append(pd.read_json(io.BytesIO(z.read(name))))
                    except Exception:
                        pass
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True, sort=False)

    raise ValueError(f"Unsupported file type for path: {path}")


def load_file_from_bytes(filename: str, content_bytes: bytes):
    """
    Load a file provided as bytes (filename used to detect type).
    Returns pandas.DataFrame
    """
    lower = filename.lower()
    if lower.endswith(".csv"):
        return _read_csv_bytes(content_bytes)

    if lower.endswith((".xlsx", ".xls")):
        return _read_excel_bytes(content_bytes)

    if lower.endswith(".json"):
        return _read_json_bytes(content_bytes)

    if lower.endswith(".txt"):
        try:
            return pd.read_csv(io.BytesIO(content_bytes), sep=None, engine="python")
        except Exception:
            return pd.read_csv(io.BytesIO(content_bytes))

    if lower.endswith(".zip"):
        frames = []
        with zipfile.ZipFile(io.BytesIO(content_bytes), "r") as z:
            for name in z.namelist():
                if name.lower().endswith(".csv"):
                    try:
                        frames.append(pd.read_csv(io.BytesIO(z.read(name))))
                    except Exception:
                        pass
                elif name.lower().endswith((".xlsx", ".xls")):
                    try:
                        frames.append(pd.read_excel(io.BytesIO(z.read(name))))
                    except Exception:
                        pass
                elif name.lower().endswith(".json"):
                    try:
                        frames.append(pd.read_json(io.BytesIO(z.read(name))))
                    except Exception:
                        pass
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True, sort=False)

    # For .db and .sql we require a file on disk (can't reasonably load from bytes here),
    # raise informative error so callers can write bytes to a temp file and call load_file()
    if lower.endswith((".db", ".sqlite", ".sql")):
        raise ValueError("For .db/.sql files, save bytes to a temporary file and call load_file(path).")

    raise ValueError(f"Unsupported file type for filename: {filename}")
