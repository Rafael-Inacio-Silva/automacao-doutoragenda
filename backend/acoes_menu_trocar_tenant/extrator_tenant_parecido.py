from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def extrator_tenant_parecido(driver):
    print("🔎 Extraindo apenas tenants disponíveis...")

    try:
        wait = WebDriverWait(driver, 10)

        titulo_tenants_disponiveis = wait.until(
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
            print("❌ Mensagem encontrada: Nenhum tenant encontrado")
            return ["Nenhum tenant encontrado"]

        elementos = driver.find_elements(
            By.XPATH,
            "//*[normalize-space(text())='Tenants Disponíveis']"
            "/following::*[starts-with(normalize-space(text()), '#')]"
        )

        resultados = []

        for elemento in elementos:
            texto = elemento.text.strip()

            if not texto:
                continue

            primeira_linha = texto.split("\n")[0].strip()

            if not primeira_linha.startswith("#"):
                continue

            if primeira_linha not in resultados:
                resultados.append(primeira_linha)
                print(f"✅ Tenant disponível encontrado: {primeira_linha}")

        if not resultados:
            print("⚠️ Nenhum tenant disponível extraído")
            return []

        return resultados

    except TimeoutException:
        print("⚠️ Tempo esgotado para localizar a área de Tenants Disponíveis")
        return []

    except Exception as e:
        print(f"⚠️ Erro ao extrair tenants disponíveis: {e}")
        return []