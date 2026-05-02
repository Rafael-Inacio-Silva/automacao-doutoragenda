from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_campo_selecione_tenant_trocar(driver):
    print("🖱️ Tentando clicar no combobox do tenant atual...")

    elemento = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//h2[contains(., 'Trocar de Tenant')]/following::*[@role='combobox'][1]"
            )
        )
    )

    elemento.click()

    print("✅ Clique realizado com sucesso")
    return True