from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_botao_tenant(driver):
    print("🖱️ Tentando clicar no botão tenant...")

    botao = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//header//button[contains(., "Tenant")]')
        )
    )

    botao.click()

    print("✅ Botão tenant clicado com sucesso.")
    return True