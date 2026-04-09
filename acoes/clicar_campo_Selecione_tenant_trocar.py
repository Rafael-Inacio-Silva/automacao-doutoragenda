from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_campo_Selecione_tenant_trocar(driver):
    print("🖱️ Tentando clicar no botão...")

    elemento = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="radix-_r_m_"]'))
    )

    elemento.click()

    print("✅ Clique realizado com sucesso")
    return True