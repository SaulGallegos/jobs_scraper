from logs import insert_log, is_job_in_log
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import json
import re
import time


BASE_URLS = [
    "https://www.occ.com.mx/empleos/en-jalisco/en-la-ciudad-de-guadalajara/",
    "https://www.occ.com.mx/empleos/en-ciudad-de-mexico/",
    "https://www.occ.com.mx/empleos/en-aguascalientes/",
    "https://www.occ.com.mx/empleos/en-nuevo-leon/en-la-ciudad-de-monterrey/",
    "https://www.occ.com.mx/empleos/en-queretaro/",
    "https://www.occ.com.mx/empleos/en-puebla/",
    "https://www.occ.com.mx/empleos/en-morelos/",
    "https://www.occ.com.mx/empleos/en-sonora/",
    "https://www.occ.com.mx/empleos/en-chihuahua/",
    "https://www.occ.com.mx/empleos/en-coahuila/",
]
NUMBER_OF_PAGES = 15


def initialized_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--window-size=1920x1080')

    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps({
            'recentDestinations': [{
                'id': 'Save as PDF',
                'origin': 'local',
                'account': '',
            }],
            'selectedDestinationId': 'Save as PDF',
            'version': 2,
            'isCssBackgroundEnabled': True,
            'isHeaderFooterEnabled': False,
        })
    }
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')

    service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def get_job_information(driver):
    wait_load = WebDriverWait(driver, 1)
    title = wait_load.until(
        lambda driver: driver.find_element(By.XPATH, "//div[@class='jobHeaderDesktop-0-2-503']"))
    description = wait_load.until(
        lambda driver: driver.find_element(By.XPATH, "//div[@class='descriptionContainer-0-2-505']"))
    return title.text, description.text


def get_pdf_from_url(driver, url):
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    pdf = driver.execute_cdp_cmd("Page.printToPDF", {
        "landscape": False,
        "printBackground": True,
        "pageSize": "A4"
    })

    return pdf


class OccScraper:
    def __init__(self):
        self.driver = initialized_driver()
        self.driver.get(BASE_URLS[0])

    def save_pdf(self, pdf, id):
        file_path = f'datasets/occ/pdf/{id}.pdf'
        with open(file_path, "wb") as file:
            file.write(base64.b64decode(pdf['data']))
        return file_path

    def get_jobs_url_by_page(self, base_index, page):
        self.driver.get(BASE_URLS[base_index] + f'?page={page}')
        wait_load = WebDriverWait(self.driver, 0.5)
        jobs_list = wait_load.until(
            lambda driver: driver.find_elements(By.XPATH, "//div[@class='card-0-2-520 flat-0-2-522 card-0-2-558']"))
        jobs_list = [job.find_element(
            By.XPATH, ".//a").get_attribute('href') for job in jobs_list]
        print(
            f'Page {page} has {len(jobs_list)} jobs. Location: {BASE_URLS[base_index]}')

        current_jobs = json.load(open('occ_jobs_url.json', 'r'))
        jobs_list += current_jobs
        jobs_list = list(dict.fromkeys(jobs_list))

        print(f'Total jobs: {len(jobs_list)}')

        with open('occ_jobs_url.json', 'w') as json_file:
            json.dump(jobs_list, json_file)

    def get_jobs_url(self, base_index):
        for page in range(1, NUMBER_OF_PAGES + 1):
            self.get_jobs_url_by_page(base_index, page)

    def save_all_jobs_url(self):
        for base_index in range(len(BASE_URLS)):
            self.get_jobs_url(base_index)

    def get_all_jobs_information(self, path):
        jobs_list = []
        with open(path, 'r') as json_file:
            jobs_list = json.load(json_file)

        for job_url in jobs_list:
            job_log_info = {
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "platform": "occ",
            }

            match = re.search(r'/(\d+-[a-zA-Z0-9-]+)', job_url)  # "ID"

            self.driver.get(job_url)
            title, description = get_job_information(self.driver)

            if match:
                job_log_info['id'] = match.group(1)
            else:
                print("Pattern not found")

            if not is_job_in_log(job_log_info['id']):
                html = self.driver.page_source
                html_path = f'datasets/occ/html/{job_log_info["id"]}.html'
                with open(html_path, 'w') as html_file:
                    job_log_info['html_path'] = html_path
                    html_file.write(html)

                txt_path = f'datasets/occ/text/{job_log_info["id"]}.txt'
                with open(txt_path, 'w') as txt_file:
                    job_log_info['txt_path'] = txt_path
                    txt_file.write(title + '\n')
                    txt_file.write(description)

                pdf = get_pdf_from_url(self.driver, job_url)
                pdf_path = self.save_pdf(pdf, job_log_info['id'])
                job_log_info['pdf_path'] = pdf_path

                insert_log(job_log_info)
                print(f'Saved job: {job_log_info["id"]}')

    def close_driver(self):
        self.driver.close()
