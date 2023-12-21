from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from src.utils.dirs import get_pdf_from_url, save_pdf
from src.utils.initial_driver import initialized_driver
from src.utils.logs import insert_log, is_job_in_log
import time

NUMBER_OF_JOBS = 7063


class JaliscoTrabajaScraper:
    def __init__(self):
        self.driver = initialized_driver()
        self.driver.get(
            'https://www.jaliscotrabaja.com.mx')

    def login(self):
        open_modal_button = self.driver.find_element(
            By.XPATH, '//form[@class="d-flex btn-login"]/button[1]')
        open_modal_button.send_keys(Keys.RETURN)
        time.sleep(1)
        username_input = self.driver.find_element(
            By.XPATH, '//input[@id="login-email"]')
        password_input = self.driver.find_element(
            By.XPATH, '//input[@id="login-password"]')
        time.sleep(1)
        username_input.send_keys('viyabat117@bayxs.com')
        password_input.send_keys('McSQm6d6qTLrQ.R')
        time.sleep(1)
        login_button = self.driver.find_element(
            By.ID, "btnLogin")
        login_button.send_keys(Keys.RETURN)
        time.sleep(1)

    def scrape_page(self, job_id):
        self.driver.get(
            'https://www.jaliscotrabaja.com.mx/candidato/includes/bolsa_trabajo/data-bolsa_trabajo_vacante_info.php?idvacante=' + str(job_id))
        wait_load = WebDriverWait(self.driver, 1)

        title = wait_load.until(
            lambda driver: driver.find_element(By.XPATH, "//h2[@class='card-title']"))
        description = wait_load.until(
            lambda driver: driver.find_element(By.XPATH, "//div[@class='col-sm-6 vacante-info']"))

        job_log_info = {
            'id': job_id,
            'platform': 'jaliscotrabaja',
            'date': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        if is_job_in_log(str(job_id)):
            html = self.driver.page_source
            html_path = f'datasets/jaliscotrabaja/html/{job_id}.html'
            with open(html_path, 'w') as html_file:
                job_log_info['html_path'] = html_path
                html_file.write(html)

            txt_path = f'datasets/jaliscotrabaja/text/{job_log_info["id"]}.txt'
            with open(txt_path, 'w') as txt_file:
                job_log_info['txt_path'] = txt_path
                txt_file.write(title.text + '\n')
                txt_file.write(description.text)

            pdf = get_pdf_from_url(
                self.driver, 'https://www.jaliscotrabaja.com.mx/candidato/includes/bolsa_trabajo/data-bolsa_trabajo_vacante_info.php?idvacante=' + str(job_id))
            job_log_info['pdf_path'] = save_pdf(
                pdf, job_log_info['id'], 'jaliscotrabaja')

            print('Job saved: ' + str(job_id))
            insert_log(job_log_info)

    def scrape_all_jobs(self):
        self.login()
        for i in range(150, NUMBER_OF_JOBS + 1):
            self.scrape_page(i)

    def close_driver(self):
        self.driver.close()
