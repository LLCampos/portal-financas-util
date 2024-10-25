import logging
from configparser import ConfigParser
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

from util import login

config = ConfigParser()
config.read("conf.ini")

chrome_options = webdriver.ChromeOptions()
preferences = {"directory_upgrade": True,
               "safebrowsing.enabled": True}
chrome_options.add_experimental_option("prefs", preferences)


def create_fatura_recibo():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    logging.info("Entering page.")
    driver.get(config.get("portal_financas", "url_emitir_facturas"))

    login(driver, config)

    logging.info("Filling form.")

    # Date
    today = datetime.today()

    invoice_date = datetime(today.year, today.month, today.day)
    invoice_date_str = invoice_date.strftime("%Y-%m-%d")
    invoice_date_field = driver.find_element(By.XPATH, "//input[@name='dataPrestacao']")
    invoice_date_field.send_keys(invoice_date_str)

    # Type of invoice
    driver.find_element(By.XPATH, "//option[@label='Fatura-Recibo']").click()

    radio_button_to_click = driver.find_element(By.XPATH, "//label/input[@value=1]/..")
    assert radio_button_to_click.text == "Pagamento dos bens ou dos serviços"
    radio_button_to_click.click()

    # Info about company
    company_country = config.get('company', "company_country").upper()
    driver.find_element(By.XPATH, f"//option[contains(@label, '{company_country}')]").click()

    company_code_field = driver.find_element(By.XPATH, "//input[@name='nifEstrangeiro']")
    company_code_field.send_keys(config.get("company", "company_code"))

    company_name_field = driver.find_element(By.XPATH, "//input[@name='nomeAdquirente']")
    company_name_field.send_keys(config.get("company", "company_name"))

    button_morada_cliente = driver.find_element(By.ID, "buttonMoradaCliente")
    button_morada_cliente.click()
    sleep(1)

    company_address = config.get("company", "company_address")
    address_field = driver.find_element(By.XPATH, "//textarea[@name='moradaAdqClienteL']")
    address_field.send_keys(company_address)

    company_postal_code = config.get("company", "company_postal_code")
    postal_code_field = driver.find_element(By.XPATH, "//input[@name='codPostalAdqCliente']")
    postal_code_field.send_keys(company_postal_code)

    company_city = config.get("company", "company_city")
    city_field = driver.find_element(By.XPATH, "//input[@name='localidadeAdqCliente']")
    city_field.send_keys(company_city)


    bens_servicos_element = driver.find_element(By.ID, "Bens&ServicosFT")
    bens_servicos_adicionar_button = bens_servicos_element.find_element(By.XPATH, ".//button[contains(text(), 'Adicionar')]")
    bens_servicos_adicionar_button.click()

    sleep(1)

    tipo_input = driver.find_element(By.XPATH, "//select[@name='tipoProduto']")
    Select(tipo_input).select_by_visible_text("Serviço")

    tipo_ref_input = driver.find_element(By.XPATH, "//select[@name='tipoRef']")
    Select(tipo_ref_input).select_by_visible_text("Outro")

    referencia_input = driver.find_element(By.XPATH, "//input[@name='referencia']")
    referencia_input.send_keys("Serviço de desenvolvimento de software")

    descricao_input = driver.find_element(By.XPATH, "//textarea[@name='descricao']")
    descricao_input.send_keys("Serviço de desenvolvimento de software")

    unidade_input = driver.find_element(By.XPATH, "//select[@name='unidade']")
    Select(unidade_input).select_by_visible_text("mês - Mês")

    salary = str(int(config.get("company", "salary")) * 100)
    preco_unitario_input = driver.find_element(By.XPATH, "//input[@name='precoUnit']")
    preco_unitario_input.send_keys(salary)

    taxa_iva_input = driver.find_element(By.XPATH, "//select[@name='taxaIVA']")
    Select(taxa_iva_input).select_by_visible_text("0%")

    motivo_isencao_input = driver.find_element(By.XPATH, "//select[@name='motivoIsencaoLinha']")
    Select(motivo_isencao_input).select_by_visible_text("IVA - autoliquidação - Artigo 6.º n.º 6 alínea a) do CIVA, a contrário")

    sleep(1)
    adicionar_produtos_modal = driver.find_element(By.ID, "adicionarProdutosModal")
    guardar_button = adicionar_produtos_modal.find_element(By.XPATH, "//button[text()='Guardar']")
    guardar_button.click()

    button_pagamento = driver.find_element(By.ID, "buttonPagamento")
    button_pagamento.click()
    sleep(1)

    pagamento_element = driver.find_element(By.ID, "pagamento")
    pagamento_adicionar_button = pagamento_element.find_element(By.XPATH, ".//button[contains(text(), 'Adicionar')]")
    pagamento_adicionar_button.click()

    sleep(1)

    payment_method_select = driver.find_element(By.XPATH, "//select[@name='formaPagamento']")
    Select(payment_method_select).select_by_visible_text("Transferência Bancária")

    guardar_button = driver.find_element(By.XPATH, "//button[text()='Guardar']")
    guardar_button.click()

    sleep(1)

    driver.find_element(By.XPATH, "//button[text() = 'Emitir']").click()
    sleep(1)
    driver.find_element(By.XPATH, "//div[@class = 'modal-dialog']//button[text() = 'Emitir']").click()

    sleep(2)

    logging.info("Invoice created.")
    driver.close()


if __name__ == "__main__":
    create_fatura_recibo()
