from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_aba_conversa(driver):
    """
    Clica na aba Conversa dentro da tela de Visualizar/Gerenciar Agente.

    Usa um XPath flexível:
    - procura pela aba com role='tab'
    - aceita id que contenha '-trigger-conversation'
    - ou texto visível 'Conversa'
    """

    print("🖱️ Tentando clicar na aba Conversa...")

    xpath_aba_conversa = (
        '//*[@role="tab" '
        'and (contains(@id, "-trigger-conversation") '
        'or contains(normalize-space(.), "Conversa"))]'
    )

    aba_conversa = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, xpath_aba_conversa)
        )
    )

    try:
        aba_conversa.click()
    except Exception:
        driver.execute_script("arguments[0].click();", aba_conversa)

    print("✅ Aba Conversa clicada com sucesso.")
    return True