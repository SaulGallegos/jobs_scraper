
from occScraper import OccScraper
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
    if not os.path.exists('logs.csv'):
        with open('logs.csv', 'w') as file:
            file.write('id, platform, date, text_path, html_path, pdf_path\n')


if __name__ == "__main__":
    initialize_dirs()

    occ_scraper = OccScraper()
    # occ_scraper.save_all_jobs_url()
    occ_scraper.get_all_jobs_information('occ_jobs_url.json')
    occ_scraper.close_driver()
