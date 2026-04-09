from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def extrator_tenant_parecido(driver):
    print("🔎 Extraindo resultados de tenant...")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Tenants Disponíveis')]"))
        )

        # verifica se apareceu "Nenhum tenant encontrado"
        elementos_nao_encontrado = driver.find_elements(
            By.XPATH,
            "//*[contains(text(), 'Nenhum tenant encontrado')]"
        )

        if elementos_nao_encontrado:
            print("❌ Mensagem encontrada: Nenhum tenant encontrado")
            return ["Nenhum tenant encontrado"]

        # pega todos os spans/divs que começam com #
        elementos = driver.find_elements(
            By.XPATH,
            "//*[starts-with(normalize-space(text()), '#')]"
        )

        resultados = []

        for elemento in elementos:
            texto = elemento.text.strip()
            if texto and texto not in resultados:
                resultados.append(texto)
                print(f"✅ Resultado encontrado: {texto}")

        if not resultados:
            print("⚠️ Nenhum resultado extraído")
            return []

        return resultados

    except TimeoutException:
        print("⚠️ Tempo esgotado para localizar os resultados")
        return []

    except Exception as e:
        print(f"⚠️ Erro ao extrair tenants: {e}")
        return []