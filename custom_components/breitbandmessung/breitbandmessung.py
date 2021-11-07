#!/usr/bin/env python3

import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .downloader import download as webdriver_download

class BreitbandException(Exception):
    """Something went wrong"""
    pass

class Breitbandmessung:
    SERVICE_URL = "https://www.breitbandmessung.de/test"
    WAIT_TIMEOUT = 30
    RESULT_TIMEOUT = 90

    """Class to do the tests"""
    def __init__(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            service = Service(webdriver_download(False))
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.element_wait = WebDriverWait(self.driver, Breitbandmessung.WAIT_TIMEOUT)
            self.result_wait = WebDriverWait(self.driver, Breitbandmessung.RESULT_TIMEOUT)
        except Exception as ex:
            raise BreitbandException(ex) from ex

    def run(self):
        try:
            self.driver.get(Breitbandmessung.SERVICE_URL)
            self.element_wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'modal-dialog-centered')))
            self.element_wait.until(EC.element_to_be_clickable((By.ID, 'allow-necessary'))).click()
            self.element_wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-primary'))).click()
            self.element_wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Akzeptieren']")))
            server_text = self.element_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rtt-info"))).text
            server = None
            match = re.search(r'Die Laufzeit wird zu Servern in (\w+) gemessen', server_text)
            if match:
                server = match.groups()[0]
            self.result_wait.until(EC.presence_of_element_located((By.XPATH, "//h1[text()='Die Browsermessung ist abgeschlossen.']")))

            ping = self.driver.find_element(By.XPATH, "//span[@class='title' and text()='Laufzeit']/parent::div/following-sibling::div/span").text
            download = self.driver.find_element(By.XPATH, "//span[@class='title' and text()='Download']/parent::div/following-sibling::div/span").text
            upload = self.driver.find_element(By.XPATH, "//span[@class='title' and text()='Upload']/parent::div/following-sibling::div/span").text
            test_id = self.driver.find_element(By.XPATH, "//div/table/tbody/tr[5]/td[3]").text

        except Exception as ex:
            raise BreitbandException(ex) from ex

        return {
            'test_id': test_id,
            'server': server,
            'ping': ping,
            'download': download,
            'upload': upload,
        }


    def quit(self):
        try:
            self.driver.quit()
        except Exception as ex:
            raise BreitbandException(ex) from ex
