from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def inserir_id_e_nome_medico(driver, id_medico, nome_medico):
    """
    Preenche o campo Nome do tenant.
    """

    texto_formatado = f"{id_medico} - {nome_medico}"
    print(f"⌨️ Tentando preencher o campo com: {texto_formatado}")

    campo = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[name='name'][placeholder='Nome do tenant']")
        )
    )

    campo.click()
    campo.clear()
    campo.send_keys(texto_formatado)

    print("✅ Campo preenchido com send_keys.")
    return True