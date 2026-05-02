import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


# ============================================================
# NAVEGADOR
# ============================================================

def iniciar_chrome():
   options = Options()
   #options.add_argument("--headless=new")  # modo invisível moderno
   options.add_argument("--start-maximized")
   options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

   driver = webdriver.Chrome(options=options)
   return driver


def acessar_link(driver, url):
    """
    Acessa o link informado.

    Usa time.sleep porque, no Safari, o document.readyState pode indicar
    que carregou, mas o Quasar/Vue ainda pode estar recriando elementos.
    """

    driver.get(url)
    time.sleep(1)

    print(f"Link acessado: {driver.current_url}")


# ============================================================
# LOGIN
# ============================================================

def preencher_email_extrator(driver, email):
    """
    Preenche o campo de e-mail.

    Esta versão usa find_element direto, igual ao fluxo antigo que funcionava.
    Isso evita erro de referência perdida no Safari.
    """
    time.sleep(1)
    campo_email = driver.find_element(By.XPATH, '//input[@type="email"]')
    campo_email.click()
    campo_email.clear()
    campo_email.send_keys(email)

    print(f"E-mail preenchido: {email}")


def limpar_campo_senha_extrator(driver, tamanho_senha):
    """
    Apaga a senha atual usando backspace.

    Mantido porque, nesse sistema, o campo de senha pode não limpar
    corretamente apenas com clear().
    """
    time.sleep(1)
    campo_senha = driver.find_element(By.XPATH, '//input[@type="password"]')
    campo_senha.click()

    for _ in range(tamanho_senha + 1):
        campo_senha.send_keys(Keys.BACKSPACE)

    print("Senha anterior apagada.")


def preencher_senha_extrator(driver, senha):
    """
    Preenche o campo de senha.
    """

    campo_senha = driver.find_element(By.XPATH, '//input[@type="password"]')
    campo_senha.click()
    campo_senha.send_keys(senha)

    print("Senha preenchida.")


def clicar_continuar_extrator(driver):
    """
    Clica no botão continuar.
    """

    botao = driver.find_element(
        By.XPATH,
        '//*[@id="q-app"]/div/div/main/div[2]/div/form/button/span[2]'
    )

    botao.click()

    print("Botão continuar clicado.")


def credencial_invalida(driver, tempo=3):
    """
    Verifica se apareceu a mensagem de credenciais inválidas.
    """

    try:
        WebDriverWait(driver, tempo).until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(@class,"q-notification__message") and contains(text(),"Credenciais inválidas")]'
                )
            )
        )

        return True

    except TimeoutException:
        return False


def login_bem_sucedido(driver, tempo=8):
    """
    Confirma se o login realmente deu certo.

    O sinal de sucesso é encontrar o menu Assistentes.
    """

    try:
        WebDriverWait(driver, tempo).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="q-app"]/div/div[2]/aside/div/div[2]/div[1]/div/div[3]/a[1]/div[2]/span[1]'
                )
            )
        )

        return True

    except TimeoutException:
        return False


def login_no_link(driver, url, email, senhas, registrar=None):
    """
    Tenta fazer login em um link usando todas as senhas.

    Retorna True apenas se o login realmente entrar no sistema.

    Importante:
    - Este método NÃO deve registrar erro no front quando usado como tentativa intermediária.
    - No fluxo principal, use registrar=None nas tentativas dos links.
    """

    print(f"Acessando link: {url}")

    acessar_link(driver, url)

    if registrar:
        registrar(
            "login",
            "executando",
            "Acessando link para login",
            {
                "link": url,
                "url_atual": driver.current_url,
            },
        )

    try:
        preencher_email_extrator(driver, email)

    except Exception as erro:
        print(f"Não conseguiu preencher o e-mail no link: {url}")
        print(erro)

        if registrar:
            registrar(
                "login",
                "erro",
                "Não conseguiu preencher o e-mail",
                {
                    "link": url,
                    "erro": str(erro),
                },
            )

        return False

    for i, senha in enumerate(senhas):
        tentativa = i + 1

        print(f"Tentando senha {tentativa} no link: {url}")

        if registrar:
            registrar(
                "login",
                "executando",
                f"Tentando login com a senha {tentativa}",
                {
                    "link": url,
                    "tentativa": tentativa,
                },
            )

        try:
            if i == 0:
                preencher_senha_extrator(driver, senha)

            else:
                limpar_campo_senha_extrator(driver, len(senhas[i - 1]))
                preencher_senha_extrator(driver, senha)

            clicar_continuar_extrator(driver)

        except Exception as erro:
            print(f"Erro ao preencher senha ou clicar continuar no link: {url}")
            print(erro)

            if registrar:
                registrar(
                    "login",
                    "erro",
                    "Erro ao preencher senha ou clicar em continuar",
                    {
                        "link": url,
                        "tentativa": tentativa,
                        "erro": str(erro),
                    },
                )

            return False

        if credencial_invalida(driver):
            print(f"Senha {tentativa} inválida.")

            if registrar:
                registrar(
                    "login",
                    "alerta",
                    f"Senha {tentativa} inválida",
                    {
                        "link": url,
                        "tentativa": tentativa,
                    },
                )

            continue

        if login_bem_sucedido(driver):
            print(f"Login realizado com sucesso no link: {url}")

            if registrar:
                registrar(
                    "login",
                    "concluido",
                    "Login realizado com sucesso",
                    {
                        "link": url,
                        "tentativa": tentativa,
                    },
                )

            return True

        print(f"Senha {tentativa} não mostrou erro, mas também não confirmou login.")

        if registrar:
            registrar(
                "login",
                "alerta",
                "Senha não mostrou erro, mas o sistema não confirmou login",
                {
                    "link": url,
                    "tentativa": tentativa,
                },
            )

    print(f"Não foi possível logar no link: {url}")

    if registrar:
        registrar(
            "login",
            "erro",
            "Não foi possível logar nesse link",
            {
                "link": url,
            },
        )

    return False


# ============================================================
# MENU ASSISTENTES / PROMPTS
# ============================================================

def clicar_menu_assistentes(driver):
    """
    Clica no menu Assistentes.
    """

    wait = WebDriverWait(driver, 15)

    menu = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="q-app"]/div/div[2]/aside/div/div[2]/div[1]/div/div[3]/a[1]/div[2]/span[1]',
            )
        )
    )

    menu.click()

    print("Menu Assistentes clicado.")


def localizar_botoes_lapis(driver):
    """
    Localiza os botões de edição dos assistentes.
    """

    wait = WebDriverWait(driver, 15)

    botoes_lapis = wait.until(
        EC.presence_of_all_elements_located(
            (
                By.XPATH,
                '//*[@id="tableGPTAssistants"]/div[1]/table/tbody/tr/td[2]/div/div/button[1]/span[2]/i',
            )
        )
    )

    return botoes_lapis


def extrair_dom_do_bloco_prompt(driver):
    """
    Extrai o conteúdo do textarea de instruções/prompt.
    """

    wait = WebDriverWait(driver, 15)

    elemento = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//textarea[@name="instructions"]')
        )
    )
    time.sleep(3)
    dados = driver.execute_script(
        """
        const el = arguments[0];

        return {
            outerHTML: el.outerHTML,
            innerHTML: el.innerHTML,
            textContent: el.textContent,
            value: el.value || null
        };
        """,
        elemento,
    )

    return dados


def fechar_modal_prompt(driver):
    """
    Fecha o modal do prompt.
    """

    wait = WebDriverWait(driver, 5)

    try:
        botao_fechar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//button[contains(@class, "q-btn") and .//span[contains(text(), "Fechar")]]',
                )
            )
        )

        botao_fechar.click()

        print("Modal fechado pelo botão Fechar.")

    except Exception:
        print("Não encontrou botão Fechar. Voltando com driver.back().")
        driver.back()


def extrair_todos_os_prompts(driver, registrar=None):
    """
    Entra no menu Assistentes e extrai todos os prompts encontrados.
    """

    wait = WebDriverWait(driver, 15)
    resultados = []

    clicar_menu_assistentes(driver)

    try:
        botoes = localizar_botoes_lapis(driver)

    except TimeoutException:
        print("Nenhum botão de edição encontrado.")

        if registrar:
            registrar(
                "extracao",
                "alerta",
                "Logou, mas não encontrou assistentes para extração",
                {
                    "total_assistentes": 0,
                },
            )

        return resultados

    total = len(botoes)

    print(f"{total} assistente(s) encontrado(s).")

    if registrar:
        registrar(
            "extracao",
            "executando",
            f"{total} assistente(s) encontrado(s) para extração",
            {
                "total_assistentes": total,
            },
        )

    for i in range(total):
        botoes = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    '//*[@id="tableGPTAssistants"]/div[1]/table/tbody/tr/td[2]/div/div/button[1]/span[2]/i',
                )
            )
        )

        atual = i + 1

        print(f"Abrindo assistente {atual} de {total}.")

        if registrar:
            registrar(
                "extracao",
                "executando",
                f"Abrindo assistente {atual} de {total}",
                {
                    "assistente_atual": atual,
                    "total_assistentes": total,
                },
            )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            botoes[i],
        )

        driver.execute_script("arguments[0].click();", botoes[i])
        time.sleep(3)
        dados = extrair_dom_do_bloco_prompt(driver)
        resultados.append(dados)

        valor = dados.get("value") or ""

        print(
            f"Prompt do assistente {atual} extraído. "
            f"Tamanho: {len(valor)} caracteres."
        )

        if registrar:
            registrar(
                "extracao",
                "concluido",
                f"Prompt do assistente {atual} extraído",
                {
                    "assistente_atual": atual,
                    "total_assistentes": total,
                    "tamanho_prompt": len(valor),
                },
            )

        fechar_modal_prompt(driver)

    return resultados