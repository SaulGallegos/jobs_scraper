from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from .utils.dirs import get_pdf_from_url, save_pdf
from .utils.initial_driver import initialized_driver
from .utils.logs import insert_log, is_job_in_log
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
NUMBER_OF_PAGES = 1


def get_job_information(driver):
    wait_load = WebDriverWait(driver, 1)
    title = wait_load.until(
        lambda driver: driver.find_element(By.XPATH, "//div[@class='jobHeaderDesktop-0-2-503']"))
    description = wait_load.until(
        lambda driver: driver.find_element(By.XPATH, "//div[@class='descriptionContainer-0-2-505']"))
    return title.text, description.text


class OccScraper:
    def __init__(self):
        print("Initializing OCC scraper")
        self.driver = initialized_driver()
        self.driver.get(BASE_URLS[0])

    def get_jobs_url_by_page(self, base_index, page):
        self.driver.get(BASE_URLS[base_index] + f'?page={page}')
        wait_load = WebDriverWait(self.driver, 0.5)
        jobs_list = wait_load.until(
            lambda driver: driver.find_elements(By.XPATH, "//div[@class='card-0-2-520 flat-0-2-522 card-0-2-558']"))
        jobs_list = [job.find_element(
            By.XPATH, ".//a").get_attribute('href') for job in jobs_list]
        print(
            f'Page {page} has {len(jobs_list)} jobs. Location: {BASE_URLS[base_index]}')

        current_jobs = json.load(open('./datasets/occ_jobs_url.json', 'r'))
        jobs_list += current_jobs
        jobs_list = list(dict.fromkeys(jobs_list))

        print(f'Total jobs: {len(jobs_list)}')

        with open('./datasets/occ_jobs_url.json', 'w') as json_file:
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
                pdf_path = save_pdf(pdf, job_log_info['id'], 'occ')
                job_log_info['pdf_path'] = pdf_path

                insert_log(job_log_info)
                print(f'Saved job: {job_log_info["id"]}')

    def close_driver(self):
        self.driver.close()
