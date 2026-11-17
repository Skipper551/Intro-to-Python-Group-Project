"""Group 4 - <module>: <one sentence: what this module does>.

Authors: <Wktor, Zuzia, Natan>
"""
import pandas as pd

def _known_customers(df):
    """Return a copy of df with only the rows that have a CustomerID, as int."""
    return df.dropna(subset=["CustomerID"]).astype({"CustomerID": int})


def _main_country(customers):
    """Return a Series {CustomerID: country} using each customer's most frequent country.

    A few customers appear with more than one country. A tie goes to the
    alphabetically first country.
    """
    counts = customers.groupby(["CustomerID", "Country"]).size().reset_index(name="lines")
    counts = counts.sort_values(["lines", "Country"], ascending=[False, True])
    return counts.drop_duplicates("CustomerID").set_index("CustomerID")["Country"]


def customer_profile(df, customer_id):
    """Return a summary of one customer.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        customer_id (int): the customer's number, e.g. 12347

    Returns:
        dict: with the keys
            "customer_id" (int),
            "country" (str): the customer's most frequent country,
            "n_orders" (int): number of unique invoices,
            "total_spent" (float): sum of Revenue in GBP, rounded to 2 decimals,
            "first_purchase", "last_purchase" (pd.Timestamp),
            "favourite_product" (str): description with the most units bought

    Raises:
        ValueError: if customer_id is not in df

    Example:
        >>> customer_profile(df, 12347)["n_orders"]
        7
    """
    customers = _known_customers(df)
    rows = customers[customers["CustomerID"] == customer_id]
    if rows.empty:
        raise ValueError(f"unknown customer: {customer_id}")

    units = rows.groupby("Description")["Quantity"].sum()
    return {"customer_id": int(customer_id),
            "country": _main_country(rows).iloc[0],
            "n_orders": int(rows["InvoiceNo"].nunique()),
            "total_spent": round(float(rows["Revenue"].sum()), 2),
            "first_purchase": rows["InvoiceDate"].min(),
            "last_purchase": rows["InvoiceDate"].max(),
            "favourite_product": units.idxmax()}


def best_customers(df, n=10):
    """Return the n customers who spent the most.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        n (int): how many customers to return, at least 1. If n is larger
            than the number of customers, all customers are returned.

    Returns:
        pd.DataFrame: columns CustomerID, country, total_spent, n_orders,
            sorted by total_spent from the highest, with index 0, 1, 2...

    Raises:
        ValueError: if n is not a whole number of at least 1

    Example:
        >>> best_customers(df, n=3)["CustomerID"].tolist()
        [14646, 18102, 17450]
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be a whole number of at least 1, got {n}")

    customers = _known_customers(df)
    summary = customers.groupby("CustomerID").agg(total_spent=("Revenue", "sum"),
                                                  n_orders=("InvoiceNo", "nunique"))
    summary["total_spent"] = summary["total_spent"].round(2)
    summary["country"] = _main_country(customers)

    summary = summary.reset_index().sort_values(["total_spent", "CustomerID"],
                                                ascending=[False, True])
    return summary[["CustomerID", "country", "total_spent", "n_orders"]].head(n).reset_index(drop=True)


def customer_segments(df, vip=5000, regular=1000):
    """Split customers into segments by their total spending.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        vip (float): a customer who spent at least this much is "VIP"
        regular (float): a customer who spent at least this much, but less
            than vip, is "regular"; anyone below it is "occasional"

    Returns:
        dict: {"VIP": [ids], "regular": [ids], "occasional": [ids]} with
            CustomerIDs (int) in ascending order; a segment may be an empty list

    Raises:
        ValueError: if vip <= regular

    Example:
        >>> sorted(customer_segments(df))
        ['VIP', 'occasional', 'regular']
    """
    if vip <= regular:
        raise ValueError(f"vip must be greater than regular, got vip={vip}, regular={regular}")

    spent = _known_customers(df).groupby("CustomerID")["Revenue"].sum().round(2)
    return {"VIP": spent[spent >= vip].index.tolist(),
            "regular": spent[(spent >= regular) & (spent < vip)].index.tolist(),
            "occasional": spent[spent < regular].index.tolist()}