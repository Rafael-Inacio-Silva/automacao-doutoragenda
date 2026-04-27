from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_trocar_tenant(driver):
    print("🖱️ Tentando clicar em Trocar Tenant...")

    elemento = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//div[@role="menuitem" and normalize-space()="Trocar Tenant"]'
            )
        )
    )

    elemento.click()

    print("✅ Clique realizado com sucesso")
    return True