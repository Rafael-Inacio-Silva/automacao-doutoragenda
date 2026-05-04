import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _extrair_numero_estagio(texto):
    """
    Extrai o número de textos como:
    - Estágio 1
    - Estágio 2
    - Estágio 10
    """

    if not texto:
        return None

    encontrado = re.search(r"Estágio\s+(\d+)", texto, re.IGNORECASE)

    if encontrado:
        return encontrado.group(1)

    return None


def _extrair_indice_html_stage_name(input_nome, indice_fallback):
    """
    Extrai o índice HTML do campo:
    stage-name-0
    stage-name-1
    stage-name-2

    Esse índice é importante porque a instrução correspondente usa:
    stage-instruction-0
    stage-instruction-1
    stage-instruction-2
    """

    id_input = input_nome.get_attribute("id") or ""

    encontrado = re.search(r"stage-name-(\d+)", id_input)

    if encontrado:
        return encontrado.group(1)

    return str(indice_fallback)


def _extrair_valor_campo(elemento):
    """
    Extrai valor de input ou textarea.
    Primeiro tenta value.
    Depois tenta text.
    """

    if elemento is None:
        return ""

    valor = elemento.get_attribute("value")

    if valor is None:
        valor = elemento.text

    if valor is None:
        valor = ""

    return valor.strip()


def extrair_estagios_conversa(driver):
    """
    Extrai todos os estágios da aba Conversa.

    Dados extraídos:
    - número do estágio
    - nome preenchido no campo Nome do estágio
    - instrução correspondente do estágio

    Exemplo:
    stage-name-0        -> nome do estágio 1
    stage-instruction-0 -> instrução do estágio 1
    """

    print("🔎 Extraindo estágios da aba Conversa...")

    wait = WebDriverWait(driver, 10)

    resultado = {
        "status": "executado",
        "quantidade": 0,
        "estagios": [],
        "mensagem": "",
    }

    try:
        wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[contains(@id, "-content-conversation")]',
                )
            )
        )

        time.sleep(1)

        containers_possiveis = driver.find_elements(
            By.XPATH,
            '//*[@id="radix-_r_bn_-content-conversation"]/div/div[2]/div[1]/div[2]',
        )

        if not containers_possiveis:
            containers_possiveis = driver.find_elements(
                By.XPATH,
                '//*[contains(@id, "-content-conversation")]//div[contains(@class, "space-y-4")]',
            )

        if containers_possiveis:
            container = containers_possiveis[0]
        else:
            container = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[contains(@id, "-content-conversation")]',
                    )
                )
            )

        inputs_nome_estagio = container.find_elements(
            By.XPATH,
            './/input[starts-with(@id, "stage-name-") or @placeholder="Nome do estágio"]',
        )

        estagios = []

        for indice_visual, input_nome in enumerate(inputs_nome_estagio, start=1):
            nome_estagio = _extrair_valor_campo(input_nome)

            indice_html = _extrair_indice_html_stage_name(
                input_nome=input_nome,
                indice_fallback=indice_visual - 1,
            )

            numero_estagio = None
            texto_estagio = ""

            try:
                card_estagio = input_nome.find_element(
                    By.XPATH,
                    './ancestor::div[contains(@class, "border") and contains(@class, "rounded")][1]',
                )

                h5_estagio = card_estagio.find_element(
                    By.XPATH,
                    './/h5[contains(normalize-space(.), "Estágio")]',
                )

                texto_estagio = h5_estagio.text.strip()
                numero_estagio = _extrair_numero_estagio(texto_estagio)

            except Exception:
                card_estagio = container
                numero_estagio = str(indice_visual)
                texto_estagio = f"Estágio {indice_visual}"

            instrucao_estagio = ""

            try:
                textarea_instrucao = card_estagio.find_element(
                    By.XPATH,
                    f'.//textarea[@id="stage-instruction-{indice_html}"]',
                )

                instrucao_estagio = _extrair_valor_campo(textarea_instrucao)

            except Exception:
                try:
                    textarea_instrucao = container.find_element(
                        By.XPATH,
                        f'.//textarea[@id="stage-instruction-{indice_html}"]',
                    )

                    instrucao_estagio = _extrair_valor_campo(textarea_instrucao)

                except Exception:
                    instrucao_estagio = ""

            estagios.append(
                {
                    "numero": numero_estagio or str(indice_visual),
                    "titulo": texto_estagio or f"Estágio {indice_visual}",
                    "nome": nome_estagio,
                    "indice_html": indice_html,
                    "id_nome": f"stage-name-{indice_html}",
                    "id_instrucao": f"stage-instruction-{indice_html}",
                    "instrucao": instrucao_estagio,
                }
            )

        resultado["quantidade"] = len(estagios)
        resultado["estagios"] = estagios

        if estagios:
            resultado["mensagem"] = "Estágios e instruções extraídos com sucesso."
            print(f"✅ {len(estagios)} estágio(s) extraído(s) com sucesso")
        else:
            resultado["mensagem"] = "Nenhum estágio foi encontrado na aba Conversa."
            print("⚠️ Nenhum estágio encontrado na aba Conversa")

        return resultado

    except Exception as erro:
        resultado["status"] = "erro"
        resultado["mensagem"] = f"Erro ao extrair estágios da aba Conversa: {erro}"
        resultado["erro"] = str(erro)

        print(f"❌ Erro ao extrair estágios da aba Conversa: {erro}")
        return resultado