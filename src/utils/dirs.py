from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import os


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def initialize_dirs():
    create_dir('datasets')
    create_dir('datasets/occ')
    create_dir('datasets/occ/text')
    create_dir('datasets/occ/html')
    create_dir('datasets/occ/pdf')
    create_dir('datasets/indeed')
    create_dir('datasets/indeed/text')
    create_dir('datasets/indeed/html')
    create_dir('datasets/indeed/pdf')
    create_dir('datasets/jaliscotrabaja')
    create_dir('datasets/jaliscotrabaja/text')
    create_dir('datasets/jaliscotrabaja/html')
    create_dir('datasets/jaliscotrabaja/pdf')
    if not os.path.exists('logs.csv'):
        with open('datasets/logs.csv', 'w') as file:
            file.write('id, platform, date, text_path, html_path, pdf_path\n')
    if not os.path.exists('datasets/occ_jobs_url.json'):
        with open('datasets/occ_jobs_url.json', 'w') as file:
            file.write('[]')
    if not os.path.exists('datasets/indeed_jobs_url.json'):
        with open('datasets/indeed_jobs_url.json', 'w') as file:
            file.write('[]')


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


def save_pdf(pdf, id, platform):
    file_path = f'datasets/{platform}/pdf/{id}.pdf'
    with open(file_path, "wb") as file:
        file.write(base64.b64decode(pdf['data']))
    return file_path
