from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def clicar_opcao_gerencia_tenant(driver):
    """
    Clica no item abaixo do 'Trocar Tenant'
    XPath alvo:
    //*[@id="radix-_r_9_"]/div[7]/div[2]
    """

    print("🖱️ Tentando clicar na nova opção do menu...")

    elemento = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="radix-_r_9_"]/div[7]/div[2]')
        )
    )

    elemento.click()

    print("✅ Clique realizado com sucesso.")
    return True