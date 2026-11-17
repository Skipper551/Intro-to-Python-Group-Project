"""retail_tools - the class library written by the students of Introduction to Python and ML,
2026/27, group w03, in classes 3+4 (10 Nov 2026). Each module is one project group's work:

    cleaning.py   group 1 - Darya Ramankova, Lena Starnawska, Malcolm Swim, Wiktor Zeszut
    products.py   group 2 - Hubert Śliwowski, Filip Stańczyk, Jan Spychalski
    countries.py  group 3 - Maksym Tykhyi, Adam Szcześniak, Jan Rutkowski
    customers.py  group 4 - Wiktor Tarchalski, Zuzanna Skirska, Natan Smogór
    timeline.py   group 5 - Mikołaj Michno, Dzmitry Salenik, Agata Zuzanna Zięba
    reports.py    group 6 - Natalia Woźniczak, Łukasz Sędzikowski, Yehor Sandratskyi

Usage:
    import retail_tools as rt
    clean, report = rt.cleaning.clean_retail(raw)
    rt.products.top_products(clean, n=5)
"""
from . import cleaning, products, countries, customers, timeline, reports
