from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def clicar_primeiro_tenant(driver):
    print("🖱️ Procurando primeiro tenant disponível...")

    try:
        wait = WebDriverWait(driver, 10)

        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[normalize-space(text())='Tenants Disponíveis']"
                )
            )
        )

        print("✅ Área 'Tenants Disponíveis' localizada.")

        elementos_nao_encontrado = driver.find_elements(
            By.XPATH,
            "//*[normalize-space(text())='Tenants Disponíveis']"
            "/following::*[contains(normalize-space(text()), 'Nenhum tenant encontrado')]"
        )

        if elementos_nao_encontrado:
            print("❌ Nenhum tenant encontrado.")
            return False

        primeiro_tenant = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "("
                    "//*[normalize-space(text())='Tenants Disponíveis']"
                    "/following::*[@role='menuitem' and .//*[starts-with(normalize-space(text()), '#')]]"
                    ")[1]"
                )
            )
        )

        texto = primeiro_tenant.text.strip().split("\n")[0]
        print(f"✅ Primeiro tenant disponível encontrado: {texto}")

        primeiro_tenant.click()

        print("✅ Primeiro tenant disponível clicado com sucesso.")
        return True

    except TimeoutException:
        print("⚠️ Tempo esgotado para localizar o primeiro tenant disponível.")
        return False

    except Exception as e:
        print(f"⚠️ Erro ao clicar no primeiro tenant disponível: {e}")
        return False