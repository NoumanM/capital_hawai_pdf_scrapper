import csv
import os
import time
from glob import glob
import requests
from lxml.html import fromstring
# import seleniumwire.undetected_chromedriver as uc_wire
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

working_dir = os.getcwd()
download_dir_path = os.path.join(working_dir, 'downloaded_pdfs')
firefox_driver_path = os.path.join(working_dir, 'geckodriver.exe')
done_urls_csv_path = os.path.join(working_dir, 'done_url.csv')
if not os.path.exists(download_dir_path):
    os.mkdir(download_dir_path)


def create_firefox_driver(healdess=False):
    try:
        firefox_options = Options()
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", download_dir_path)
        firefox_options.set_preference("browser.helperApps.alwaysAsk.force", False)
        firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("services.sync.prefs.sync.browser.download.manager.showWhenStarting", False)
        firefox_options.set_preference("browser.download.useDownloadDir", True)
        firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        firefox_options.set_preference("pdfjs.disabled", True)

        driver = webdriver.Firefox(service=Service(executable_path=firefox_driver_path), options=firefox_options)

        driver.maximize_window()
        time.sleep(3)
        driver.get("https://www.capitol.hawaii.gov/sessions/session2024/Testimony/")
        return driver
    except Exception as e:
        print(e)
        print("----Got Exception----")


def get_selenium_wire_driver(headless=False):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36")
        options.add_argument('--no-sandbox')
        options.add_argument("--log-level=3")
        if headless:
            options.add_argument('--headless')
        prefs = {"profile.default_content_settings.popups": 0,
                 "download.default_directory": f"{download_dir_path}",
                 "download.prompt_for_download": False,
                 "download.directory_upgrade": True}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--start-maximized')
        chrome_exe_path = ChromeDriverManager().install()
        driver = webdriver.Chrome(service=Service(executable_path=chrome_exe_path), options=options)
        stealth(driver,
                user_agent='DN',
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        driver.get("https://www.capitol.hawaii.gov/sessions/session2024/Testimony/")
        return driver
    except Exception as e:
        print(e)
        print('------------------- Generation the New Driver')
        get_selenium_wire_driver(headless=False)


def main(url):
    payload = {}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.status_code)
    book_path = os.path.join(download_dir_path, url.split('/')[-1].lower())
    with open(book_path, 'wb') as book_file:
        book_file.write(response.content)
    print(f'PDF file downloaded: {book_path}')


def write_data_in_csv_file(data_list, file_name):
    csv_file_name = os.path.join(working_dir, f'{file_name}.csv')
    exist = False
    if os.path.exists(csv_file_name):
        exist = True
    with open(csv_file_name, 'a+', newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        for d in data_list:
            if not exist:
                writer.writerow(d.keys())
            writer.writerow(d.values())


def download_pdfs():
    downloaded_pdfs = [pdf.split('\\')[-1] for pdf in glob(os.path.join(download_dir_path, '*.pdf'))]
    done_urls = []
    if os.path.exists(done_urls_csv_path):
        with open(done_urls_csv_path, 'r') as infile:
            reader = csv.reader(infile)
            done_urls.append(row[0] for row in reader)

    driver = create_firefox_driver()
    pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.PDF')]")
    try:
        for link in pdf_links:
            pdf_name = link.get_attribute('text')
            if pdf_name in downloaded_pdfs:
                continue
            pdf_url = link.get_attribute('href')
            if pdf_url in done_urls:
                continue
            print('PDF NAME: ', pdf_name)
            link.click()
            time.sleep(5)
            write_data_in_csv_file([{'url': pdf_url}], 'done_url')
    except Exception as e:
        write_data_in_csv_file([{'exception': str(e)}], 'error')
    driver.quit()
    print('Process Ended')


if __name__ == '__main__':
    download_pdfs()
