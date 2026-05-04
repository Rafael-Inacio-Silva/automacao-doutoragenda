from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def clicar_botao_trocar_tenant(driver):
    print("🖱️ Tentando clicar no botão Trocar...")

    try:
        wait = WebDriverWait(driver, 10)

        botao_trocar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[normalize-space(.)='Trocar']"
                )
            )
        )

        botao_trocar.click()

        print("✅ Botão Trocar clicado com sucesso.")
        return True

    except TimeoutException:
        print("⚠️ Tempo esgotado para localizar o botão Trocar.")
        return False

    except Exception as e:
        print(f"⚠️ Erro ao clicar no botão Trocar: {e}")
        return False