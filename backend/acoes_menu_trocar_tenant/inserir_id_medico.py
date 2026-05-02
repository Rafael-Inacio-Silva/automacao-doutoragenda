from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def inserir_id_medico(driver, id_medico):
    print(f"⌨️ Tentando preencher o campo com: {id_medico}")

    campo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'input[placeholder="Buscar tenant..."]')
        )
    )

    campo.click()
    campo.clear()
    campo.send_keys(id_medico)

    print("✅ Campo preenchido com sucesso")
    return True