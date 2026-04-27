from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def fechar_modal_tenant(driver):
    print("🖱️ Tentando fechar modal do tenant...")

    try:
        botao_fechar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[data-slot="dialog-close"]')
            )
        )

        driver.execute_script("arguments[0].click();", botao_fechar)

        print("✅ Modal fechado com sucesso.")
        return True

    except TimeoutException:
        print("⚠️ Tempo esgotado ao tentar fechar modal.")
        return False

    except Exception as e:
        print(f"⚠️ Erro ao fechar modal: {e}")
        return False