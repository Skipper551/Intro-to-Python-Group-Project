"""Group 6 - reports: ready-made charts and a country dashboard for the Online Retail data.

Every function returns the matplotlib object it drew on (Axes or Figure),
so you can test it or change the chart afterwards.

Authors: Natalia Woźniczak, Łukasz Sędzikowski,Yehor Sandratskyi
"""
import pandas as pd
import matplotlib.pyplot as plt


VALID_PERIODS = ["D", "W", "M", "Q"]


def plot_bar(data, title, top=10):
    """Draw a horizontal bar chart from a dict or a pandas Series.

    The biggest value is shown at the top of the chart.

    Args:
        data (dict or pd.Series): labels -> numbers, e.g. {"France": 209715, "Germany": 228867}
        title (str): title of the chart
        top (int): how many of the biggest values to show (default 10)

    Returns:
        matplotlib.axes.Axes: the chart

    Raises:
        ValueError: if data is not a dict or Series, if data is empty, or if top < 1

    Example:
        >>> ax = plot_bar({"a": 3, "b": 5}, "My chart")
    """
    # 1. check the input
    if not isinstance(data, (dict, pd.Series)):
        raise ValueError("data must be a dict or a pandas Series")
    if len(data) == 0:
        raise ValueError("data is empty - nothing to plot")
    if top < 1:
        raise ValueError("top must be at least 1")

    # 2. turn a dict into a Series, so both inputs work the same way
    series = pd.Series(data)

    # 3. keep only the biggest values
    series = series.sort_values(ascending=False)
    series = series.head(top)

    # 4. reverse the order, because barh draws the first value at the bottom
    series = series.iloc[::-1]

    # 5. draw
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(series.index.astype(str), series.values)
    ax.set_title(title)
    ax.set_xlabel("Value")
    plt.tight_layout()
    return ax


def plot_revenue_trend(df, period="M", country=None):
    """Draw a line chart of revenue over time.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean), needs the
            columns InvoiceDate, Revenue and Country
        period (str): "D" (day), "W" (week), "M" (month) or "Q" (quarter). Default "M"
        country (str or None): only this country, e.g. "France". None = all countries

    Returns:
        matplotlib.axes.Axes: the chart

    Raises:
        ValueError: if period is not D/W/M/Q, or if the country is not in the data

    Example:
        >>> ax = plot_revenue_trend(df, period="M", country="Germany")
    """
    # 1. check the input
    if period not in VALID_PERIODS:
        raise ValueError(f"period must be one of {VALID_PERIODS}, got {period!r}")
    if country is not None and country not in df["Country"].unique():
        raise ValueError(f"unknown country: {country!r}")

    # 2. keep only one country if asked
    data = df
    if country is not None:
        data = df[df["Country"] == country]

    # 3. add up revenue per period
    periods = data["InvoiceDate"].dt.to_period(period)
    revenue = data.groupby(periods)["Revenue"].sum()

    # 4. draw
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(revenue.index.astype(str), revenue.values, marker="o")

    if country is None:
        ax.set_title(f"Revenue per period ({period}) - all countries")
    else:
        ax.set_title(f"Revenue per period ({period}) - {country}")
    ax.set_xlabel("Period")
    ax.set_ylabel("Revenue (GBP)")
    ax.tick_params(axis="x", rotation=90)
    plt.tight_layout()
    return ax


def country_dashboard(df, country):
    """Draw one 2x2 dashboard for one country.

    The four charts are:
        top left:     monthly revenue (line)
        top right:    top 5 products by revenue (bars)
        bottom left:  number of orders per weekday (bars)
        bottom right: distribution of order values (histogram)

    One order = one unique InvoiceNo. Order value = sum of Revenue on that invoice.

    Args:
        df (pd.DataFrame): Online Retail data (after basic_clean)
        country (str): country name exactly as in the data, e.g. "Netherlands"

    Returns:
        matplotlib.figure.Figure: the figure with 4 charts (fig.axes has 4 elements)

    Raises:
        ValueError: if the country is not in the data

    Example:
        >>> fig = country_dashboard(df, "France")
    """
    # 1. check the input
    if country not in df["Country"].unique():
        raise ValueError(f"unknown country: {country!r}")

    # 2. keep only this country
    data = df[df["Country"] == country]

    # 3. prepare the 4 small tables
    # 3a. revenue per month
    months = data["InvoiceDate"].dt.to_period("M")
    monthly_revenue = data.groupby(months)["Revenue"].sum()

    # 3b. top 5 products by revenue
    product_revenue = data.groupby("Description")["Revenue"].sum()
    top5 = product_revenue.sort_values(ascending=False).head(5)
    top5 = top5.iloc[::-1]  # biggest at the top of the chart

    # 3c. orders per weekday (count unique invoices, not rows)
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                     "Friday", "Saturday", "Sunday"]
    weekdays = data["InvoiceDate"].dt.day_name()
    orders_per_weekday = data.groupby(weekdays)["InvoiceNo"].nunique()
    orders_per_weekday = orders_per_weekday.reindex(weekday_order, fill_value=0)

    # 3d. value of each order
    order_values = data.groupby("InvoiceNo")["Revenue"].sum()

    # 4. draw the 2x2 figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    ax1 = axes[0, 0]
    ax2 = axes[0, 1]
    ax3 = axes[1, 0]
    ax4 = axes[1, 1]

    ax1.plot(monthly_revenue.index.astype(str), monthly_revenue.values, marker="o")
    ax1.set_title("Monthly revenue (GBP)")
    ax1.tick_params(axis="x", rotation=90)

    ax2.barh(top5.index, top5.values)
    ax2.set_title("Top 5 products by revenue (GBP)")

    ax3.bar(orders_per_weekday.index, orders_per_weekday.values)
    ax3.set_title("Number of orders per weekday")
    ax3.tick_params(axis="x", rotation=45)

    ax4.hist(order_values, bins=30)
    ax4.set_title("Distribution of order values (GBP)")
    ax4.set_xlabel("Order value (GBP)")
    ax4.set_ylabel("Number of orders")

    fig.suptitle(f"Dashboard - {country}", fontsize=16)
    fig.tight_layout()
    return fig
