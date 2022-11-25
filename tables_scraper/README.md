# Tables Scraper
## a helper module to scrapes tables from both static and dynamic web pages

## usage:

```python
from tables_scraper import TablesScraper

response = TablesScraper.scrape_static_page("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population")
if response.succeed and len(response.tables):
    print(response.tables[0].head())
else:
    print(f"Something went wrong: {response.msg}")

"""
Rank Country / Dependency  Population                        Date Source (official or from the United Nations)                                              Notes
  Rank Country / Dependency     Numbers % of the world         Date Source (official or from the United Nations)                                              Notes
0    –                World  7994219000           100%  25 Nov 2022                             UN projection[3]                                                NaN
1    1                China  1412600000            NaN  31 Dec 2021                         Official estimate[4]  The population figure refers to mainland China...
2    2                India  1375586000            NaN   1 Mar 2022                       Official projection[5]  The figure includes the population of the Indi...
3    3        United States   336312556            NaN  24 Nov 2022                          Population clock[6]  The figure includes the 50 states and the Dist...
4    4            Indonesia   275773800            NaN   1 Jul 2022                         Official estimate[7]                                                NaN
"""
```

```python
from tables_scraper import TablesScraper

URL = "https://coinmarketcap.com/"
DRIVER_PATH = r"C:\Users\username\Downloads\chromedriver.exe"

response = TablesScraper.scrape_static_page(URL, DRIVER_PATH)
if response.succeed and len(response.tables):
    print(response.tables[0].head())
else:
    print(f"Something went wrong: {response.msg}")
```