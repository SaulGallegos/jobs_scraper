from src.occScraper import OccScraper
from src.indeedScraper import IndeedScraper
from src.jaliscoTrabajaScraper import JaliscoTrabajaScraper


def start_occ_scraper():
    scraper = OccScraper()
    # scraper.save_all_jobs_url()
    scraper.get_all_jobs_information('datasets/occ_jobs_url.json')
    scraper.close_driver()


def start_indeed_scraper():
    scraper = IndeedScraper()
    scraper.save_all_jobs_url()
    scraper.get_all_jobs_information('datasets/indeed_jobs_url.json')
    scraper.close_driver()


def start_jalisco_trabaja_scraper():
    scraper = JaliscoTrabajaScraper()
    scraper.scrape_all_jobs()
    scraper.close_driver()
