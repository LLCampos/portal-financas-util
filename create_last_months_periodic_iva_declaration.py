from configparser import ConfigParser
from time import sleep
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from util import login, minus_one_month

config = ConfigParser()
config.read("conf.ini")


def create_periodic_iva_declaration():
    driver = webdriver.Chrome(config.get("other", "chromedriver_path"))

    driver.get(config.get("portal_financas", "url_consultar_facturas"))
    driver.fullscreen_window()
    login(driver, config)
    sleep(2)
    tables_recibos = driver.find_elements_by_class_name("tbody-border-primary")
    assert len(tables_recibos) == 1
    table = tables_recibos[0]
    salary = int(table.find_element_by_tag_name("tr").find_elements_by_tag_name("td")[3].text.strip(" €")[:-3].replace('.', ''))

    driver.get(config.get("portal_financas", "url_declaracao_iva"))
    driver.fullscreen_window()
    #login(driver, config)
    sleep(2)

    today = datetime.today()
    today_last_month = minus_one_month(today)

    driver.find_element_by_xpath("//lf-select[@path = 'localizacaoSede']//input").send_keys("Continente" + Keys.ENTER)
    driver.find_element_by_xpath("//lf-select[@path = 'anoDeclaracao']//input").send_keys(f"{today_last_month.year}{Keys.ENTER}")
    driver.find_element_by_xpath("//lf-select[@path = 'periodoDeclaracao']//input").send_keys(today_last_month.strftime('%m') + Keys.ENTER)
    driver.find_element_by_xpath("//lf-select[@path = 'prazo']//input").send_keys("Dentro do prazo" + Keys.ENTER)

    driver.find_element_by_xpath("//span[text() = ' Apuramento ']").click()

    sim = "0"
    nao = "1"

    driver.find_element_by_xpath(f"//lf-radio[@path = 'temOperacoesComLiqImposto']//input[@value='{nao}']/../i").click()
    driver.find_element_by_xpath(f"//lf-radio[@path = 'temOperacoesSemLiqImposto']//input[@value='{sim}']/../i").click()
    driver.find_element_by_xpath(f"//lf-radio[@path = 'temOperacoesDedutiveis']//input[@value='{nao}']/../i").click()
    driver.find_element_by_xpath(f"//lf-radio[@path = 'temOperacoesAdquirenteComLiqImposto']//input[@value='{nao}']/../i").click()

    salary_formatted = str(salary * 100)
    driver.find_element_by_xpath("//lf-number[@path='btOperacoesIsentasComDeducao']//input").send_keys(salary_formatted)

    driver.find_element_by_xpath("//*[contains(@class,'navigation-conclude')]//span[contains(text(), 'Entregar')]").click()
    sleep(1)
    driver.find_element_by_xpath("//*[contains(@class,'modal-footer')]//span[contains(text(), 'Entregar')]").click()
    sleep(1)
    driver.find_element_by_xpath("//span[text() = 'Autenticar']").click()
    login(driver, config)


if __name__ == "__main__":
    create_periodic_iva_declaration()