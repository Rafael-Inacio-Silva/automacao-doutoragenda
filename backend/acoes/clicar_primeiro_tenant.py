from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def clicar_primeiro_tenant(driver):
    print("🖱️ Procurando primeiro tenant disponível...")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Tenants Disponíveis')]")
            )
        )

        elementos_nao_encontrado = driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Nenhum tenant encontrado')]"
        )

        if elementos_nao_encontrado:
            print("❌ Nenhum tenant encontrado.")
            return False

        primeiro_tenant = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '(//div[@role="menuitem" and .//div[contains(@class,"grid")] and .//span])[1]' # usado para tenant do DRia teste
                    #'(//div[@role="menuitem" and .//*[starts-with(normalize-space(), "#")]])[1]'
                )
            )
        )

        texto = primeiro_tenant.text.strip().split("\n")[0]
        print(f"✅ Primeiro tenant encontrado: {texto}")

        primeiro_tenant.click()

        print("✅ Primeiro tenant clicado com sucesso.")
        return True

    except TimeoutException:
        print("⚠️ Tempo esgotado para localizar o primeiro tenant.")
        return False

    except Exception as e:
        print(f"⚠️ Erro ao clicar no primeiro tenant: {e}")
        return False