from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def preencher_login(driver, email):
    campo_login = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input[placeholder="Telefone"]')
        )
    )
    campo_login.click()
    campo_login.clear()
    campo_login.send_keys(email)


def preencher_senha(driver, senha):
    campo_senha = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input[type="password"]')
        )
    )
    campo_senha.click()
    campo_senha.clear()
    campo_senha.send_keys(senha)


def clicar_entrar(driver):
    botao = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@type="submit" and contains(., "Acessar")]')
        )
    )
    botao.click()


def esperar_pos_login(driver):
    try:
        WebDriverWait(driver, 20).until(
            lambda d: "login" not in d.current_url.lower()
        )
        return True
    except TimeoutException:
        return False