from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def clicar_opcao_gerenciar_agentes(driver):
    print("🖱️ Tentando clicar em Gerenciar Agentes...")

    elemento = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//div[@role="menuitem" and normalize-space()="Gerenciar Agentes"]'
            )
        )
    )

    elemento.click()

    print("✅ Clique em Gerenciar Agentes realizado com sucesso")
    return True