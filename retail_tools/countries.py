"""Group 3 - countries: sales summary per country (revenue, orders, customers).

Authors: Maksym Tykhyi, Adam Szcześniak, Jan Rutkowski
"""
import pandas as pd


def country_summary(df):
    """Summarise sales for every country.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)

    Returns:
        dict: {country: {"revenue": float, "orders": int,
                         "customers": int, "avg_order_value": float}}
              orders = number of unique invoices,
              customers = number of unique CustomerID (missing IDs not counted),
              avg_order_value = revenue / orders

    Raises:
        ValueError: if df is empty

    Example:
        >>> country_summary(df)["Germany"]["customers"]
    """
    if len(df) == 0:
        raise ValueError("df is empty")

    summary = {}
    for country, group in df.groupby("Country"):
        revenue = group["Revenue"].sum()
        orders = group["InvoiceNo"].nunique()
        customers = group["CustomerID"].nunique()
        summary[country] = {"revenue": round(float(revenue), 2),
                            "orders": int(orders),
                            "customers": int(customers),
                            "avg_order_value": round(float(revenue / orders), 2)}
    return summary


def top_countries(df, n=5, by="revenue", exclude_uk=True):
    """Return the top n countries by one metric from country_summary.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        n (int): how many countries, n >= 1
        by (str): "revenue", "orders", "customers" or "avg_order_value"
        exclude_uk (bool): if True, United Kingdom is left out

    Returns:
        pd.Series: index = country, values = metric, sorted from the biggest

    Raises:
        ValueError: if n < 1 or by is not a known metric

    Example:
        >>> top_countries(df, n=3, by="customers")
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    if by not in ["revenue", "orders", "customers", "avg_order_value"]:
        raise ValueError("unknown metric: " + str(by))

    table = pd.DataFrame.from_dict(country_summary(df), orient="index")
    if exclude_uk:
        table = table.drop("United Kingdom", errors="ignore")
    return table[by].sort_values(ascending=False).head(n)


def compare_countries(df, countries):
    """Compare chosen countries side by side.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        countries (list of str): country names, e.g. ["Germany", "France"]
                                 (spelled like in the data, e.g. "EIRE")

    Returns:
        pd.DataFrame: one row per country (in the given order),
                      columns: revenue, orders, customers, avg_order_value

    Raises:
        ValueError: if a country is not in the data (the message names it)

    Example:
        >>> compare_countries(df, ["Germany", "France"])
    """
    if isinstance(countries, str):      # one name given as text -> make it a list
        countries = [countries]

    summary = country_summary(df)
    for country in countries:
        if country not in summary:
            raise ValueError("unknown country: " + str(country))

    table = pd.DataFrame.from_dict(summary, orient="index")
    return table.loc[countries]
