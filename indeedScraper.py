
from logs import insert_log, is_job_in_log
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import json
import time
import random
import undetected_chromedriver as uc


BASE_URLS = [
    'https://mx.indeed.com/jobs?q=&l=Guadalajara%2C+Jal.&from=searchOnHP&start=']
NUMBER_OF_PAGES = 2


def get_job_information(driver):
    wait_load = WebDriverWait(driver, 1)
    title = wait_load.until(
        lambda driver: driver.find_element(By.XPATH, "//div[@class='jobsearch-InfoHeaderContainer jobsearch-DesktopStickyContainer css-zt53js eu4oa1w0']"))
    description = wait_load.until(
        lambda driver: driver.find_element(By.XPATH, "//div[@class='jobsearch-BodyContainer']"))
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


class IndeedScraper:
    def __init__(self):
        self.driver = uc.Chrome()
        self.driver.get(BASE_URLS[0])

    def save_pdf(self, pdf, id):
        file_path = f'datasets/indeed/pdf/{id}.pdf'
        with open(file_path, "wb") as file:
            file.write(base64.b64decode(pdf['data']))
        return file_path

    def get_jobs_url_by_page(self, base_index, page):
        self.driver.get(BASE_URLS[base_index] + f'{page}')
        wait_load = WebDriverWait(self.driver, 0.5)
        jobs_list = wait_load.until(
            lambda driver: driver.find_elements(By.XPATH, "//div[@class='job_seen_beacon']"))
        jobs_list = [job.find_element(
            By.XPATH, ".//a").get_attribute('href') for job in jobs_list]
        print(
            f'Page {page} has {len(jobs_list)} jobs. Location: {BASE_URLS[base_index]}')

        current_jobs = json.load(open('indeed_jobs_url.json', 'r'))
        jobs_list += current_jobs
        jobs_list = list(dict.fromkeys(jobs_list))

        print(f'Total jobs: {len(jobs_list)}')

        with open('indeed_jobs_url.json', 'w') as json_file:
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
                "platform": "indeed",
            }

            self.driver.get(job_url)
            title, description = get_job_information(self.driver)

            slug = f'{random.randint(0, 100)}_' + ' '.join(title[:10]) + \
                f'_{random.randint(0, 1000)}'
            job_log_info["id"] = slug.replace(' ', '_')

            if not is_job_in_log(job_log_info['id']):
                html = self.driver.page_source
                html_path = f'datasets/indeed/html/{job_log_info["id"]}.html'
                with open(html_path, 'w') as html_file:
                    job_log_info['html_path'] = html_path
                    html_file.write(html)

                txt_path = f'datasets/indeed/text/{job_log_info["id"]}.txt'
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
