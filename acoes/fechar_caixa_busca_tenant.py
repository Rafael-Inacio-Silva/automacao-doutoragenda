from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def fechar_modal_tenant(driver):
    """
    1. Clica em qualquer ponto da tela para desfocar o campo de busca
    2. Depois clica no botão fechar do modal
    """

    print("🖱️ Desfocando campo de busca...")

    try:
        # clique em ponto neutro da tela (canto superior esquerdo)
        driver.execute_script("""
            document.elementFromPoint(20,20).click();
        """)

        print("✅ Clique fora realizado.")

        # espera botão fechar ficar clicável
        botao_fechar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="radix-_r_5_"]/button')
            )
        )

        # clique no botão fechar
        driver.execute_script("arguments[0].click();", botao_fechar)

        print("✅ Modal fechado com sucesso.")
        return True

    except TimeoutException:
        print("⚠️ Tempo esgotado ao tentar fechar modal.")
        return False

    except Exception as e:
        print(f"⚠️ Erro ao fechar modal: {e}")
        return False