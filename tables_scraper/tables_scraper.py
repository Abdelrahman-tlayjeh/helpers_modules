from urllib.error import HTTPError
from pandas import DataFrame
from _tables_scraper import extract_tables, get_js_driven_source_code
from dataclasses import dataclass
"""
TODO: add comments and documentation | Build unit tests
"""
@dataclass
class TablesScraperResponse:
    succeed:bool
    msg:str
    tables:list[DataFrame]


class TablesScraper:
    
    @staticmethod
    def scrape_static_page(url:str, visible_only:bool) -> TablesScraperResponse:
        try:
            result = extract_tables(url, visible_only)
            return TablesScraperResponse(True, "Done", result)
        except Exception as e:
            return TablesScraperResponse(False, e, [])


    @staticmethod
    def scrape_dynamic_page(url:str, driver_path:str, visible_only:bool, show_browser:bool) -> TablesScraperResponse:
        #get source code
        try:
            source = get_js_driven_source_code(url, driver_path, show_browser)
            result = extract_tables(source, visible_only)
            return TablesScraperResponse(True, "Done", result)
        except Exception as e:
            return TablesScraperResponse(False, e, [])


    @staticmethod
    def auto_scrape_tables(url:str, driver_path:str, visible_only:bool, show_browser:bool) -> TablesScraperResponse:
        response = TablesScraper.scrape_static_page(url, visible_only)
        #if 'scrape_static_page' succeed
        if response.succeed:
            return response
        #return the response of 'scrape_dynamic_page'
        return TablesScraper.scrape_dynamic_page(url, driver_path, visible_only, show_browser)