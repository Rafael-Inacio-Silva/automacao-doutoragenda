from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_botao_tenant(driver):
    """
    Clica no botão do header principal.
    XPath alvo:
    //*[@id="root"]/div/main/div/header/button
    """

    print("🖱️ Tentando clicar no botão do header...")

    botao = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="root"]/div/main/div/header/button')
        )
    )

    botao.click()

    print("✅ Botão do header clicado com sucesso.")
    return True