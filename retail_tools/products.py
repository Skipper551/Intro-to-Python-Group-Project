"""Group 2 - products: rank, look up and search products in the Online Retail data.

Authors: Hubert Sliwowski, Jan Spychalski, Filip Stanczyk
"""
import pandas as pd


# ---------------------------------------------------------------------------
# Function 1 - top_products
# ---------------------------------------------------------------------------
def top_products(df, n=10, by="revenue", country=None):
    """Return the top n products ranked by revenue or by quantity sold.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean). Needs
            Description, Quantity, Country and a Revenue or UnitPrice column.
        n (int): how many products to return, must be >= 1. Default 10.
        by (str): "revenue" or "quantity". Default "revenue".
        country (str or None): only rows from this country, e.g. "Germany".
            None = all countries.

    Returns:
        pd.DataFrame: columns Description, Quantity, Revenue, one row per
            product (grouped by Description), sorted biggest first by `by`,
            index 0..n-1. If there are fewer than n products, all are returned.

    Raises:
        ValueError: if n is not an integer >= 1, `by` is not "revenue"/"quantity",
            or `country` is not in the data.

    Example:
        >>> top_products(df, n=5, country="Germany")
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be an integer >= 1, got {n!r}")

    sort_column = {"revenue": "Revenue", "quantity": "Quantity"}
    if by not in sort_column:
        raise ValueError(f"by must be 'revenue' or 'quantity', got {by!r}")

    if country is not None:
        if country not in df["Country"].unique():        # .unique() = the VALUES (not `in df["Country"]`, that checks the index!)
            raise ValueError(f"unknown country: {country!r}")
        df = df[df["Country"] == country]

    if "Revenue" not in df.columns:                      # works also on data without a Revenue column
        df = df.assign(Revenue=df["Quantity"] * df["UnitPrice"])   # assign() makes a copy - the caller's df is not changed

    result = (df.groupby("Description")[["Quantity", "Revenue"]].sum()
                .sort_values(sort_column[by], ascending=False)
                .head(n)
                .reset_index())                          # Description back from the index to a column; index 0..n-1
    return result


# ---------------------------------------------------------------------------
# Function 2 - product_info
# ---------------------------------------------------------------------------
def product_info(df, stock_code):
    """Return a summary of one product.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        stock_code (str): product code, e.g. "85123A" (an int like 22423 also works)

    Returns:
        dict: {
            "stock_code": str,
            "description": str or None - the most common description of this code,
            "units_sold": int - total quantity sold,
            "revenue": float - total revenue in GBP, rounded to 2 decimals,
            "n_customers": int - number of unique known customers (rows without CustomerID are not counted),
            "n_countries": int - number of countries it was sold to,
            "avg_unit_price": float - average price per unit sold (revenue / units_sold), rounded to 2 decimals
        }

    Raises:
        ValueError: if stock_code does not appear in df

    Example:
        >>> product_info(df, "85123A")["description"]
        'WHITE HANGING HEART T-LIGHT HOLDER'
    """
    code = str(stock_code).strip().upper()          # 22423 -> "22423", " 85123a " -> "85123A"
    rows = df[df["StockCode"].str.upper() == code]       # case-insensitive: "85123a" rows belong to 85123A too

    if rows.empty:
        raise ValueError(f"unknown stock_code: {stock_code!r}")

    descriptions = rows["Description"].dropna()
    description = descriptions.mode().iloc[0] if not descriptions.empty else None

    units_sold = int(rows["Quantity"].sum())
    revenue = float(rows["Revenue"].sum())

    return {
        "stock_code": code,
        "description": description,
        "units_sold": units_sold,
        "revenue": round(revenue, 2),
        "n_customers": int(rows["CustomerID"].nunique()),   # nunique() skips missing IDs
        "n_countries": int(rows["Country"].nunique()),
        "avg_unit_price": round(revenue / units_sold, 2),
    }


# ---------------------------------------------------------------------------
# Function 3 - search_products
# ---------------------------------------------------------------------------
def search_products(df, keyword):
    """Find all product descriptions containing a keyword.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        keyword (str): text to look for; matched case-insensitively as a
            plain substring (no regex), e.g. "heart" also finds "HEARTS"

    Returns:
        list of str: sorted list of unique matching descriptions ([] if none)

    Raises:
        ValueError: if df is not a DataFrame, or keyword is not a non-empty string

    Example:
        >>> search_products(df, "lantern")[:2]
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")
    if not isinstance(keyword, str) or not keyword.strip():
        raise ValueError(f"keyword must be a non-empty string, got {keyword!r}")

    descriptions = df["Description"].dropna()                                  # missing descriptions would crash .str
    mask = descriptions.str.contains(keyword, case=False, regex=False)        # regex=False: "(" and "." are normal characters
    return sorted(descriptions[mask].unique())


# ---------------------------------------------------------------------------
# Extra - remove_non_products
# ---------------------------------------------------------------------------
# Shipping codes that DO contain a digit, so the "no digits" rule alone misses them
SHIPPING_CODES = {"C2", "23444"}      # C2 = CARRIAGE, 23444 = Next Day Carriage


def remove_non_products(df):
    """Return a copy of df without postage, fees and manual adjustments.

    Rule: a row is removed if its StockCode has no digits (POST, DOT, M, AMAZONFEE,
    BANK CHARGES, B, S...) or is a shipping code (C2 = CARRIAGE, 23444 = Next Day Carriage).
    Limitation: the "no digits" rule also removes 3 small real products
    (DCGSSBOY, DCGSSGIRL party bags and PADS, ~300 GBP in total).

    Args:
        df (pd.DataFrame): Online Retail data with a StockCode column.

    Returns:
        pd.DataFrame: copy of df with the same columns, without rows like POSTAGE,
            DOTCOM POSTAGE, CARRIAGE, Manual, AMAZON FEE.

    Raises:
        ValueError: if df has no StockCode column.
    """
    if "StockCode" not in df.columns:
        raise ValueError("df has no 'StockCode' column")

    has_digit = df["StockCode"].str.contains(r"\d", na=False)
    is_shipping = df["StockCode"].isin(SHIPPING_CODES)
    return df[has_digit & ~is_shipping].copy()
