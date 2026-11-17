"""Group 1 - cleaning: find and remove problems in the raw Online Retail data.
Authors: Darya Ramankova, Lena Starnawska, Malcolm Swim, Wiktor Zeszut
"""

import pandas as pd

# stock codes that are NOT products (we found them in the data, class Task 10)
NOT_PRODUCTS = ["POST", "DOT", "C2", "M", "m", "D", "S", "B",
                "BANK CHARGES", "AMAZONFEE", "CRUK"]



def quality_report(df):
    """Count the problems in the data, without removing anything.
    Args:
        df (pd.DataFrame): raw data from load_retail()
    Returns:
        dict: number of rows with each problem
    Raises:
        ValueError: if df is empty
    """
    # empty table -> error
    if len(df) == 0:
        raise ValueError("df is empty")
    # an empty dictionary, then we add one problem per line
    report = {}
    report["rows"] = len(df)                                                    # all rows
    report["missing_customer_id"] = int(df["CustomerID"].isna().sum())          # no customer
    report["missing_description"] = int(df["Description"].isna().sum())         # no product name
    report["cancelled_rows"] = int(df["InvoiceNo"].str.startswith("C").sum())   # "C" = cancelled
    report["non_positive_quantity"] = int((df["Quantity"] <= 0).sum())          # quantity <= 0
    report["non_positive_price"] = int((df["UnitPrice"] <= 0).sum())            # price <= 0
    report["duplicated_rows"] = int(df.duplicated().sum())                      # copied rows
    return report



def non_product_codes(df):
    """Return {stock_code: description} for codes that are not products.
    Args:
        df (pd.DataFrame): raw data from load_retail()
    Returns:
        dict: {stock_code: description}, e.g. {"POST": "POSTAGE", ...}
    Raises:
        ValueError: if df is empty
    """
    # empty table -> error
    if len(df) == 0:
        raise ValueError("df is empty")
    # keep only the rows whose code is on our NOT_PRODUCTS list
    rows = df[df["StockCode"].isin(NOT_PRODUCTS)]
    # one description per code, as a dictionary {code: description}
    return rows.groupby("StockCode")["Description"].first().to_dict()



def clean_retail(df):
    """Clean the data in 6 steps. The original df is not changed.
    Args:
        df (pd.DataFrame): raw data from load_retail()
    Returns:
        tuple: (clean_df, report) - report says how many rows each step removed,
               plus rows_before, rows_after and removed_pct
    Raises:
        ValueError: if df is empty
    """
    # empty table -> error
    if len(df) == 0:
        raise ValueError("df is empty")
    clean = df.copy()                       # work on a COPY, the original stays the same
    report = {"rows_before": len(clean)}
    # every step: remember the size -> remove rows -> save how many were removed
    before = len(clean)
    clean = clean[~clean.duplicated()]                         # 1) remove copied rows
    report["duplicates"] = before - len(clean)
    before = len(clean)
    clean = clean[clean["Description"].notna()]                # 2) remove rows without a name
    report["no_description"] = before - len(clean)
    before = len(clean)
    clean = clean[~clean["InvoiceNo"].str.startswith("C")]     # 3) remove cancellations
    report["cancelled"] = before - len(clean)
    before = len(clean)
    clean = clean[clean["Quantity"] > 0]                       # 4) keep quantity > 0
    report["quantity"] = before - len(clean)
    before = len(clean)
    clean = clean[clean["UnitPrice"] > 0]                      # 5) keep price > 0
    report["price"] = before - len(clean)
    before = len(clean)
    clean = clean[~clean["StockCode"].isin(NOT_PRODUCTS)]      # 6) remove postage, fees...
    report["non_products"] = before - len(clean)
    report["rows_after"] = len(clean)
    report["removed_pct"] = round((len(df) - len(clean)) / len(df) * 100, 2)
    return clean, report
