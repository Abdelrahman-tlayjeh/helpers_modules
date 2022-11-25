from pandas import DataFrame
from _tables_scraper import extract_tables, get_js_driven_source_code
from dataclasses import dataclass

@dataclass
class TablesScraperResponse:
    """the response of each method in TableScraper"""
    succeed:bool
    msg:str
    tables:list[DataFrame]


class TablesScraper:
    
    @staticmethod
    def scrape_static_page(url:str, visible_only:bool=True) -> TablesScraperResponse:
        """
        scrape tables from a static web page

        Params:
            - url: web page url
            - visible_only [True by default]: True to scrape only visible tables, False otherwise
        """
        try:
            result = extract_tables(url, visible_only)
            msg = "Done" if len(result) else "No Tables are found"
            return TablesScraperResponse(True, msg, result)
        except Exception as e:
            return TablesScraperResponse(False, e, [])


    @staticmethod
    def scrape_dynamic_page(url:str, driver_path:str, visible_only:bool=True, show_browser:bool=False) -> TablesScraperResponse:
        """
        scrape tables from a dynamic web page

        Params:
            - url: web page url
            - driver_path: path to the chrome driver (.exe)
            - visible_only [True by default]: True to scrape only visible tables, False otherwise
            - show_browser [False by default]: True to show the chrome browser, False to hide it.
        """
        #get source code
        try:
            source = get_js_driven_source_code(url, driver_path, show_browser)
            result = extract_tables(source, visible_only)
            msg = "Done" if len(result) else "No Tables are found"
            return TablesScraperResponse(True, msg, result)
        except Exception as e:
            return TablesScraperResponse(False, e, [])


    @staticmethod
    def auto_scrape_tables(url:str, driver_path:str, visible_only:bool=True, show_browser:bool=False) -> TablesScraperResponse:
        """
        try to scrape the web page using scrape_static_page(), if that fails, it will use scrape_dynamic_page()
        
        Params:
            - url: web page url
            - driver_path: path to the chrome driver (.exe)
            - visible_only [True by default]: True to scrape only visible tables, False otherwise
            - show_browser [False by default]: True to show the chrome browser, False to hide it.
        """
        response = TablesScraper.scrape_static_page(url, visible_only)
        #if 'scrape_static_page' succeed
        if response.succeed:
            return response
        #return the response of 'scrape_dynamic_page'
        return TablesScraper.scrape_dynamic_page(url, driver_path, visible_only, show_browser)