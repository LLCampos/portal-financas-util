import logging
from configparser import ConfigParser
from datetime import datetime
from time import sleep

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from util import login

config = ConfigParser()
config.read("conf.ini")

chrome_options = webdriver.ChromeOptions()
preferences = {"directory_upgrade": True,
               "safebrowsing.enabled": True}
chrome_options.add_experimental_option("prefs", preferences)


def create_fatura_recibo():
    driver = webdriver.Chrome(ChromeDriverManager().install())

    logging.info("Entering page.")
    driver.get(config.get("portal_financas", "url_emitir_facturas"))

    login(driver, config)

    logging.info("Filling form.")

    # Date
    today = datetime.today()

    invoice_date = datetime(today.year, today.month, today.day)
    invoice_date_str = invoice_date.strftime("%Y-%m-%d")
    invoice_date_field = driver.find_element_by_xpath("//input[@name='dataPrestacao']")
    invoice_date_field.send_keys(invoice_date_str)

    # Type of invoice
    driver.find_element_by_xpath("//option[@label='Fatura-Recibo']").click()

    radio_button_to_click = driver.find_element_by_xpath("//label/input[@value=1]/..")
    assert radio_button_to_click.text == "Pagamento dos bens ou dos serviços"
    radio_button_to_click.click()

    # Info about company
    company_country = config.get('company', "company_country").upper()
    driver.find_element_by_xpath(f"//option[contains(@label, '{company_country}')]").click()

    company_code_field = driver.find_element_by_xpath("//input[@name='nifEstrangeiro']")
    company_code_field.send_keys(config.get("company", "company_code"))

    company_name_field = driver.find_element_by_xpath("//input[@name='nomeAdquirente']")
    company_name_field.send_keys(config.get("company", "company_name"))

    description = (f'{config.get("company", "company_name")}\n'
                   f'{config.get("company", "company_address")}\n'
                   f'Co. Reg. No. {config.get("company", "company_code")}')

    description_field = driver.find_element_by_xpath("//textarea[@name='servicoPrestado']")
    description_field.send_keys(description)

    driver.find_element_by_xpath("//option[@label='Regras de localização - art.º 6.º [regras especificas]']").click()
    driver.find_element_by_xpath("//option[@label = 'Sem retenção - Não residente sem estabelecimento']").click()

    salary = str(int(config.get("company", "salary")) * 100)
    salary_field = driver.find_element_by_xpath("//input[@name='valorBase']")
    salary_field.send_keys(salary)

    driver.find_element_by_xpath("//button[text() = 'Emitir']").click()
    sleep(1)
    driver.find_element_by_xpath("//div[@class = 'modal-dialog']//button[text() = 'Emitir']").click()

    sleep(2)

    logging.info("Invoice created.")
    driver.close()


if __name__ == "__main__":
    create_fatura_recibo()
