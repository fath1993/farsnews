import os
import pickle
import threading
import time
from custom_logs.models import custom_log
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from farsnews.settings import CHROME_DRIVER_PATH, BASE_DIR
from scrapers.models import FarsNews
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
d = DesiredCapabilities.CHROME
d['goog:loggingPrefs'] = {'performance': 'ALL'}


# ------------ Start Scraper functions -------------------
def get_time_sleep():
    time_sleep = 5
    return time_sleep


def farsnews_scrap():
    options = Options()
    options.add_argument("--window-size=1920,1200")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    # options.add_argument("--headless=new")
    # options.add_argument("--disable-web-security")
    # options.add_argument("--allow-running-insecure-content")
    # options.add_argument("--ignore-certificate-errors")
    motion_array_files_path = BASE_DIR / 'media/cr/'
    prefs = {"download.default_directory": f"{motion_array_files_path}"}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=options, desired_capabilities=d)
    webdriver_problem_number_of_reloading = 0

    while True:
        try:
            number_of_get_accept_cookie_btn_tries = 0
            while True:
                try:
                    driver.get('https://farsnews.ir/economy/showcase')

                    time.sleep(10)

                    check_chrome_connection_status(driver)

                    # Disable JavaScript restrictions
                    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                        "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                          get: () => undefined
                        })
                      """
                    })
                    while True:
                        refresh_windows_handle_to_default(driver)
                        try:
                            block_of_news = driver.find_element(By.CLASS_NAME, 'n-y292xp')
                            news = block_of_news.find_elements(By.TAG_NAME, 'div')
                            for item in news:
                                refresh_windows_handle_to_default(driver)
                                new_farsnews = None
                                new_news = False
                                try:
                                    try:
                                        sub_items_1 = item.find_elements(By.CLASS_NAME, 'auto-dir-block')
                                        title = sub_items_1[0].text.strip()
                                        sub_title = sub_items_1[1].text.strip()
                                        try:
                                            FarsNews.objects.get(title=title)
                                            # print(f'news {title} exist.')
                                            continue
                                        except Exception as e:
                                            # print(f'exception 4.1: {e}')
                                            if f'{title}' != '':
                                                new_farsnews = FarsNews.objects.create()
                                                new_news = True
                                            else:
                                                continue
                                        new_farsnews.title = title
                                        new_farsnews.sub_title = sub_title
                                        print(f'title: {title}')
                                        print(f'sub_title: {sub_title}')
                                    except Exception as e:
                                        pass
                                        #print(f'exception 4: {e}')
                                    if not new_news:
                                        continue

                                    try:
                                        sub_items_2 = item.find_elements(By.CLASS_NAME, 'ms-2px')
                                        date = sub_items_2[0].text.strip()
                                        new_farsnews.date = date
                                        print(f'date: {date}')
                                    except Exception as e:
                                        print(f'exception 5: {e}')
                                        time.sleep(0.1)

                                    try:
                                        sub_items_3 = item.find_elements(By.TAG_NAME, 'a')
                                        for sub_item_3 in sub_items_3:
                                            if f'{sub_item_3.text.strip()}'.find('گزارش') != -1:
                                                try:
                                                    actions = ActionChains(driver)
                                                    actions.key_down(Keys.CONTROL).click(sub_item_3).key_up(
                                                        Keys.CONTROL).perform()
                                                    driver.switch_to.window(driver.window_handles[1])
                                                    new_window = True
                                                    x = 0
                                                    while True:
                                                        try:
                                                            WebDriverWait(driver, 5).until(
                                                                EC.presence_of_all_elements_located(
                                                                    (By.TAG_NAME, 'body')))
                                                            new_farsnews.link_of_content = driver.current_url
                                                            post_content = \
                                                            driver.find_elements(By.CLASS_NAME, 'px-post-padding-x')[0]

                                                            post_sections = post_content.find_elements(By.CLASS_NAME,
                                                                                                       'pt-1')
                                                            context_text = ''
                                                            i = 0
                                                            for post_section in post_sections:
                                                                if i > 0:
                                                                    context_text += f'{post_section.text.strip()}\n'
                                                                    print(f'context_text: {post_section.text.strip()}')
                                                                i += 1
                                                            new_farsnews.content = context_text
                                                            break
                                                        except Exception as e:
                                                            print(f'exception 7: {e}')
                                                            driver.refresh()
                                                            time.sleep(0.1)
                                                            x += 1
                                                        if x > 3:
                                                            break
                                                    time.sleep(0.1)
                                                except Exception as e:
                                                    print(f'exception 8: {e}')
                                    except Exception as e:
                                        print(f'exception 6: {e}')
                                    if new_farsnews:
                                        new_farsnews.save()
                                        print(f'new_farsnews: {new_farsnews.title}')
                                    print('---------------------------')
                                except Exception as e:
                                    print(f'exception 3: {e}')
                                    time.sleep(0.1)
                        except Exception as e:
                            print(f'exception 2: {e}')
                            time.sleep(0.1)
                        driver.execute_script("window.scrollBy(0, 500);")
                        time.sleep(0.1)
                except Exception as e:
                    print(f'exception 1: {e}')
        except NoSuchElementException as e:
            custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(1)
        except WebDriverException as e:
            custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(1)
        except ConnectionError as e:
            custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(1)
        except Exception as e:
            custom_log('motion_array_download_file webdriver exception. err: ' + str(e), f"scrapers")
            custom_log('we are waiting for ' + str(get_time_sleep()) + ' second', f"scrapers")
            time.sleep(1)
        webdriver_problem_number_of_reloading += 1
        if webdriver_problem_number_of_reloading == 3:
            driver.quit()
            custom_log("motion_array_download_file: webdriver exception caused download to be aborted", f"scrapers")
            return False


def check_chrome_connection_status(driver_object):
    for entry in driver_object.get_log('performance'):
        if str(entry['message']).find('"errorText":"net::ERR_TIMED_OUT"') != -1:
            errorText = "net::ERR_NO_SUPPORTED_PROXIES"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_NO_SUPPORTED_PROXIES"') != -1:
            errorText = "net::ERR_NO_SUPPORTED_PROXIES"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_INTERNET_DISCONNECTED"') != -1:
            errorText = "net::ERR_INTERNET_DISCONNECTED"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_TIMED_OUT"') != -1:
            errorText = "net::ERR_CONNECTION_TIMED_OUT"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_RESET"') != -1:
            errorText = "net::ERR_CONNECTION_RESET"
            custom_log(errorText, f"scrapers")
            return ConnectionError
        elif str(entry['message']).find('"errorText":"net::ERR_CONNECTION_REFUSED"') != -1:
            errorText = "net::ERR_CONNECTION_REFUSED"
            custom_log(errorText, f"scrapers")
            return ConnectionError



def refresh_windows_handle_to_default(driver):
    window_handles = driver.window_handles
    for handle in window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(window_handles[0])