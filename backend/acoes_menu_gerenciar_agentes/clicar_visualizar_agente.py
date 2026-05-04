from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clicar_visualizar_agente(driver):
    print("🖱️ Tentando clicar no botão Visualizar Agente...")

    wait = WebDriverWait(driver, 15)

    botao = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                (
                    "//button[.//*[name()='svg' "
                    "and contains(@class, 'lucide-eye') "
                    "and contains(@class, 'h-4') "
                    "and contains(@class, 'w-4')]]"
                ),
            )
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        botao,
    )

    try:
        botao.click()
    except Exception:
        driver.execute_script("arguments[0].click();", botao)

    print("✅ Clique no botão Visualizar Agente realizado com sucesso.")
    return True