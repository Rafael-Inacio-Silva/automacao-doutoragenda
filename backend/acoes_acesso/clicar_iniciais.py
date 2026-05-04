from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_elemento_iniciais(driver):
    print("🖱️ Tentando clicar nas iniciais...")

    elemento = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//button[@data-slot="dropdown-menu-trigger" and normalize-space()="RS"]'
            )
        )
    )

    elemento.click()

    print("✅ Clique nas iniciais realizado com sucesso")
    return True