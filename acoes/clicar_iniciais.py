from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_elemento_iniciais(driver):
    print("🖱️ Tentando clicar no elemento...")

    elemento = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="radix-_r_8_"]'))
    )

    elemento.click()

    print("✅ Clique realizado com sucesso")
    return True