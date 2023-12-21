from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import json


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
