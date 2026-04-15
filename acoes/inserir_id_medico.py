from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def inserir_id_medico(driver,id_medico):
    print("⌨️ Tentando preencher o campo com 'teste'...")

    campo = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="radix-_r_n_"]/div[1]/div/input'))
    )

    campo.click()
    campo.clear()
    campo.send_keys(id_medico)

    print("✅ Campo preenchido com sucesso")
    return True