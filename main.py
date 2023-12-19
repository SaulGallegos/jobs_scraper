
import occScraper
import indeedScraper
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
    if not os.path.exists('logs.csv'):
        with open('logs.csv', 'w') as file:
            file.write('id, platform, date, text_path, html_path, pdf_path\n')
    if not os.path.exists('occ_jobs_url.json'):
        with open('occ_jobs_url.json', 'w') as file:
            file.write('[]')
    if not os.path.exists('indeed_jobs_url.json'):
        with open('indeed_jobs_url.json', 'w') as file:
            file.write('[]')


def start_occ_scraper():
    scraper = occScraper.OccScraper()
    scraper.save_all_jobs_url()
    scraper.get_all_jobs_information('occ_jobs_url.json')
    scraper.close_driver()


def start_indeed_scraper():
    scraper = indeedScraper.IndeedScraper()
    scraper.save_all_jobs_url()
    scraper.get_all_jobs_information('indeed_jobs_url.json')
    scraper.close_driver()


if __name__ == "__main__":
    initialize_dirs()

    # start_occ_scraper()
    # start_indeed_scraper()
