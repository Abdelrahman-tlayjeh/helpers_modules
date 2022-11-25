"""
helpers functions used in the main module (tables_scraper)
"""

from pandas import read_html, DataFrame
from urllib.error import HTTPError, URLError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, InvalidArgumentException


def extract_tables(src:str, visible_only:bool=True) -> list[DataFrame]:
    """
    returns all tables as a list of pandas DataFrames

    Params:
        - src: a string can be either a URL or a source code
        - visible_only [True by default]: True to extract only visible tables, False to extract hidden tables as well.

    """
    try:
        return read_html(src, displayed_only=visible_only)
    #no tables are found
    except ValueError:
        return []
    except HTTPError as e:
        err = e.getcode()
        if err > 500:
            raise Exception(f"Server Error: {err}")
        if err > 400:
            raise Exception(f"Client Error: {err}")
        if err > 300:
            raise Exception(f"Redirection: {err}")
        else:
            raise Exception(f"No HTTP Error: {err}")
    except URLError:
        raise Exception(f"Invalid URL")
    except Exception as e:
        raise Exception(f"unexpected error occurred: {e}")


def init_chrome_driver(driver_path:str, show_browser:bool) -> webdriver:
    """
    instantiate and return a Chrome driver

    Params:
        - driver_path: path to the chrome driver (.exe)
        - show_browser: True to show the chrome browser, False to hide it.
    """
    #setup options
    options = Options()
    #show/hide the browser
    options.headless = not show_browser
    #change the default user-agent
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36")
    #hide Chrome console output
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #block images
    options.experimental_options["prefs"] = {"profile.default_content_setting_values":{
        "images": 2
    }}

    #! invalid path will raise an unhandled exception
    return webdriver.Chrome(driver_path, options=options)


def get_js_driven_source_code(url:str, driver_path:str, show_browser:bool=False) -> str:
    """
    return the source code of the needed page

    Params:
        - url: webpage url
        - driver_path: path to the chrome driver (.exe)
        - show_browser [False by default]: True to show the chrome browser, False otherwise.
    """
    driver = init_chrome_driver(driver_path, show_browser)
    #get the URL
    try:
        driver.get(url)
    except TimeoutException:
       raise Exception("Time Out")
    except InvalidArgumentException:
       raise Exception("Invalid URL")
    except Exception as e:
        raise Exception(f"unexpected error occurred: {e}")

    #close the driver and return the source code
    source_code = driver.page_source
    driver.quit()
    return source_code
