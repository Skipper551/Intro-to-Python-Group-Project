"""Group 5 - timeline: revenue over time (per period, busiest hour/weekday/month, one day).

Authors: <Michno Mikołaj, Salenik Dzmitry, Zięba Agata>
"""
import pandas as pd


def revenue_by_period(df, period="M", country=None):
    """Return total revenue per day (D), week (W), month (M) or quarter (Q).

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        period (str): "D", "W", "M" or "Q"
        country (str or None): only this country; None = all countries

    Returns:
        pd.Series: revenue per period, sorted by time

    Raises:
        ValueError: if period is not D/W/M/Q or the country is not in the data

    Example:
        >>> revenue_by_period(df, "Q", country="France")
    """
    if period not in ["D", "W", "M", "Q"]:
        raise ValueError(f"period must be D, W, M or Q, got {period}")
    if country is not None:
        if country not in df["Country"].values:          # is this country in the data?
            raise ValueError(f"unknown country: {country}")
        df = df[df["Country"] == country]                # keep only this country
    periods = df["InvoiceDate"].dt.to_period(period)     # date -> day/week/month/quarter
    return df.groupby(periods)["Revenue"].sum()          # add up revenue in each period


def busiest(df, unit="weekday"):
    """Return revenue per hour, weekday or month as a dict, busiest first.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        unit (str): "hour", "weekday" or "month"

    Returns:
        dict: {value: revenue}, biggest revenue first (a day with no sales, e.g. Saturday, is not in it)

    Raises:
        ValueError: if unit is not "hour", "weekday" or "month"

    Example:
        >>> busiest(df, "weekday")
    """
    options = {"hour": df["InvoiceDate"].dt.hour,             # 0-23
               "weekday": df["InvoiceDate"].dt.day_name(),    # Monday, Tuesday...
               "month": df["InvoiceDate"].dt.month_name()}    # January, February...
    if unit not in options:                                   # is this KEY in the dict?
        raise ValueError(f"unit must be hour, weekday or month, got {unit}")
    return df.groupby(options[unit])["Revenue"].sum().sort_values(ascending=False).to_dict()


def day_summary(df, date):
    """Summarise one day of sales.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        date (str): the day, e.g. "2011-12-05"

    Returns:
        dict: {"date", "n_invoices", "n_customers", "revenue", "top_product"};
        a day without sales gives zeros and None

    Raises:
        ValueError: if the date is not readable or outside the data

    Example:
        >>> day_summary(df, "2011-12-05")
    """
    day = pd.Timestamp(date).date()                  # text -> date (bad text raises ValueError)
    dates = df["InvoiceDate"].dt.date                # only the day, without the time
    if day < dates.min() or day > dates.max():
        raise ValueError(f"date {day} is outside the data ({dates.min()} - {dates.max()})")
    rows = df[dates == day]                          # only sales from this day
    if len(rows) == 0:
        return {"date": str(day), "n_invoices": 0, "n_customers": 0,
                "revenue": 0, "top_product": None}
    return {"date": str(day),
            "n_invoices": rows["InvoiceNo"].nunique(),
            "n_customers": rows["CustomerID"].nunique(),
            "revenue": round(float(rows["Revenue"].sum()), 2),
            "top_product": rows.groupby("Description")["Revenue"].sum().idxmax()}   # product with most revenue
