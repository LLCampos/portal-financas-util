from selenium.webdriver.common.by import By

def minus_one_month(date):
    if date.month == 1:
        return date.replace(month=12, year=date.year-1)
    else:
        return date.replace(month=date.month-1)


def login(driver, config):
    driver.find_elements(By.XPATH, '//span[text()="NIF"]')[0].click()
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password-nif")

    username_field.send_keys(config.get("portal_financas", "nif"))
    password_field.send_keys(config.get("portal_financas", "password"))

    driver.find_element(By.NAME, "sbmtLogin").click()
