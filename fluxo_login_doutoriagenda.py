import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def iniciar_safari():
    """
    Abre o Safari e retorna o driver.
    """
    driver = webdriver.Safari()
    driver.maximize_window()
    return driver


def abrir_doutoriagenda(driver):
    """
    Acessa a página de login do DoutorAgenda.
    """
    driver.get("https://app.doutoriagenda.com/login")
    time.sleep(1)


def preencher_login(driver, email):
    """
    Preenche o campo de login.
    """
    campo_login = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="_r_0_"]'))
    )
    campo_login.click()
    time.sleep(1)
    campo_login.clear()
    campo_login.send_keys(email)
    time.sleep(1)


def preencher_senha(driver, senha, tamanho_senha_anterior=30):
    """
    Preenche o campo de senha.
    Quando já existe senha digitada, apaga na força usando backspace.
    """
    campo_senha = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="_r_2_"]'))
    )
    campo_senha.click()
    time.sleep(1)

    for _ in range(tamanho_senha_anterior):
        campo_senha.send_keys(Keys.BACKSPACE)

    time.sleep(1)
    campo_senha.send_keys(senha)
    time.sleep(1)


def clicar_entrar(driver):
    """
    Clica no botão de entrar.
    """
    botao = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
    )
    botao.click()
    time.sleep(1)


def verificar_erro_credencial(driver):
    """
    Verifica se apareceu mensagem de erro de login/senha.
    Ajuste os textos se o site mostrar outra mensagem.
    """
    xpaths_possiveis = [
        "//*[contains(text(), 'Credenciais inválidas')]",
        "//*[contains(text(), 'credenciais inválidas')]",
        "//*[contains(text(), 'Senha inválida')]",
        "//*[contains(text(), 'senha inválida')]",
        "//*[contains(text(), 'inválido')]",
        "//*[contains(text(), 'inválida')]",
        "//*[contains(text(), 'incorreta')]",
        "//*[contains(text(), 'erro')]",
    ]

    for xpath in xpaths_possiveis:
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except TimeoutException:
            continue

    return False


def login_doutoriagenda(driver, email, senha):
    abrir_doutoriagenda(driver)
    preencher_login(driver, email)

    print(f"Tentando login para: {email}")
    preencher_senha(driver, senha, tamanho_senha_anterior=len(senha) + 5)
    clicar_entrar(driver)

    if verificar_erro_credencial(driver):
        return False, f"{email} -> erro de acesso"

    return True, f"{email} -> acesso liberado"