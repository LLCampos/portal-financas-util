from configparser import ConfigParser
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from util import login, minus_one_month

config = ConfigParser()
config.read("conf.ini")


def create_periodic_iva_declaration():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    driver.get(config.get("portal_financas", "url_consultar_facturas"))
    login(driver, config)
    sleep(2)
    driver.fullscreen_window()
    tables_recibos = driver.find_elements(By.CLASS_NAME, "tbody-border-primary")
    assert len(tables_recibos) == 1
    table = tables_recibos[0]
    salary = int(
        table.find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td")[3].text.strip(" €")[:-3].replace('.',
                                                                                                                ''))

    driver.get(config.get("portal_financas", "url_declaracao_iva"))
    driver.fullscreen_window()
    # login(driver, config)
    sleep(2)

    today = datetime.today()
    today_last_month = minus_one_month(today)

    driver.find_element(By.XPATH, "//lf-select[@path = 'localizacaoSede']//input").send_keys("Continente" + Keys.ENTER)
    driver.find_element(By.XPATH, "//lf-select[@path = 'anoDeclaracao']//input").send_keys(
        f"{today_last_month.year}{Keys.ENTER}")
    driver.find_element(By.XPATH, "//lf-select[@path = 'periodoDeclaracao']//input").send_keys(
        today_last_month.strftime('%m') + Keys.DOWN + Keys.ENTER)

    driver.find_element(By.XPATH, "//span[text() = ' Apuramento ']").click()

    sim = "0"
    nao = "1"

    driver.find_element(By.XPATH,
                        f"//lf-radio[@path = 'temOperacoesAdquirenteComLiqImposto']//input[@value='{nao}']/../i").click()

    salary_formatted = str(salary * 100)
    driver.find_element(By.XPATH, "//lf-number[@path='btOperacoesIsentasComDeducao']//input").send_keys(
        salary_formatted)

    driver.find_element(By.XPATH,
                        "//*[contains(@class,'navigation-conclude')]//span[contains(text(), 'Entregar')]").click()
    sleep(1)
    driver.find_element(By.XPATH, "//*[contains(@class,'modal-footer')]//span[contains(text(), 'Entregar')]").click()
    sleep(1)
    driver.find_element(By.XPATH, "//span[text() = 'Autenticar']").click()
    login(driver, config)
    sleep(1)


if __name__ == "__main__":
    create_periodic_iva_declaration()
