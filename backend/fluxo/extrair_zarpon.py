import os
import csv
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from backend.acoes_zarpon.extrator_prompt_zarpon import (
    iniciar_chrome,
    login_no_link,
    extrair_todos_os_prompts,
)


# Caminho da raiz do projeto
CAMINHO_RAIZ = Path(__file__).resolve().parents[2]

# Caminho do arquivo .env
CAMINHO_ENV = CAMINHO_RAIZ / ".env"

# Caminho do arquivo CSV de resultado
CAMINHO_RESULTADO_PROMPTS = CAMINHO_RAIZ / "resultado_prompts.csv"

# Caminho do arquivo de log
CAMINHO_LOG_PROMPTS = CAMINHO_RAIZ / "log_extracao_prompts.json"

load_dotenv(CAMINHO_ENV, override=True)


def criar_csv_vazio(caminho=CAMINHO_RESULTADO_PROMPTS):
    """
    Cria um CSV vazio com cabeçalho.
    Assim, mesmo se der erro em todos os e-mails,
    o botão de download baixa um arquivo válido.
    """

    with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter="|")
        cabecalho = ["email_medico"] + [f"prompt_{i}" for i in range(1, 21)]
        writer.writerow(cabecalho)


def limpar_arquivo_resultado_prompts(caminho=CAMINHO_RESULTADO_PROMPTS):
    """
    Limpa o CSV no início de uma nova execução.
    Deve ser chamada apenas uma vez por execução,
    antes do primeiro e-mail.
    """

    criar_csv_vazio(caminho)


def limpar_arquivo_log_prompts(caminho=CAMINHO_LOG_PROMPTS):
    """
    Limpa o arquivo de log no início de uma nova execução.
    Deve ser chamada apenas uma vez por execução,
    antes do primeiro e-mail.
    """

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump([], arquivo, ensure_ascii=False, indent=2)


def salvar_evento_log(evento, caminho=CAMINHO_LOG_PROMPTS):
    """
    Salva cada evento do fluxo em um arquivo JSON.
    """

    caminho = Path(caminho)

    if caminho.exists():
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                eventos = json.load(arquivo)

            if not isinstance(eventos, list):
                eventos = []

        except Exception:
            eventos = []
    else:
        eventos = []

    eventos.append(evento)

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(eventos, arquivo, ensure_ascii=False, indent=2)


def salvar_resultado_prompts(email_medico, prompts, caminho=CAMINHO_RESULTADO_PROMPTS):
    """
    Salva no CSV os prompts extraídos com sucesso.
    """

    caminho = Path(caminho)
    arquivo_existe = caminho.exists()

    with open(caminho, "a", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter="|")

        if not arquivo_existe:
            cabecalho = ["email_medico"] + [f"prompt_{i}" for i in range(1, 21)]
            writer.writerow(cabecalho)

        linha = [email_medico]

        for i in range(20):
            if i < len(prompts):
                linha.append(prompts[i])
            else:
                linha.append("")

        writer.writerow(linha)


def salvar_status_prompts(email_medico, mensagem, caminho=CAMINHO_RESULTADO_PROMPTS):
    """
    Salva no CSV o e-mail com uma mensagem de status quando:
    - não conseguiu logar;
    - logou, mas não extraiu prompt;
    - deu erro geral.
    """

    caminho = Path(caminho)
    arquivo_existe = caminho.exists()

    with open(caminho, "a", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo, delimiter="|")

        if not arquivo_existe:
            cabecalho = ["email_medico"] + [f"prompt_{i}" for i in range(1, 21)]
            writer.writerow(cabecalho)

        linha = [email_medico, mensagem]

        for _ in range(19):
            linha.append("")

        writer.writerow(linha)


def fluxo_extrair_prompts(email_medico: str, log=None):
    driver = None
    login_confirmado = False

    def registrar(etapa, status, mensagem, dados=None):
        evento = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "fluxo": "extrair_prompts",
            "etapa": etapa,
            "status": status,
            "mensagem": mensagem,
            "dados": dados or {},
        }

        print(evento)

        salvar_evento_log(evento)

        if log:
            log(evento)

    try:
        email_medico = email_medico.strip()

        if not email_medico:
            raise ValueError("E-mail do médico não informado.")

        senha1 = os.getenv("EXTRATOR_SENHA_1")
        senha2 = os.getenv("EXTRATOR_SENHA_2")
        senha3 = os.getenv("EXTRATOR_SENHA_3")
        senha4 = os.getenv("EXTRATOR_SENHA_4")

        link1 = os.getenv("EXTRATOR_LINK_1", "https://app.driagenda.com/#/auth/login")
        link2 = os.getenv("EXTRATOR_LINK_2", "https://app.zarpon.com.br/#/auth/login")

        senhas = [senha1, senha2, senha3, senha4]
        senhas = [senha for senha in senhas if senha]

        if not senhas:
            raise ValueError(
                f"Nenhuma senha do extrator foi encontrada no arquivo .env. "
                f"Caminho verificado: {CAMINHO_ENV}"
            )

        registrar(
            "inicio",
            "executando",
            "Iniciando extração de prompts",
            {
                "email_medico": email_medico,
                "env_carregado": str(CAMINHO_ENV),
            },
        )

        registrar(
            "navegador",
            "executando",
            "Abrindo navegador",
            {
                "email_medico": email_medico,
            },
        )

        driver = iniciar_chrome()

        registrar(
            "navegador",
            "concluido",
            "Navegador iniciado",
            {
                "email_medico": email_medico,
            },
        )

        # =====================================================
        # LOGIN
        # Primeiro tenta o link 1.
        # Se não conseguir, tenta o link 2.
        # Só registra o resultado final no front depois das duas tentativas.
        # =====================================================

        registrar(
            "login",
            "executando",
            "Tentando realizar login",
            {
                "email_medico": email_medico,
            },
        )

        link_usado = None

        print("Tentando login no primeiro link...")

        login_realizado = login_no_link(
            driver=driver,
            url=link1,
            email=email_medico,
            senhas=senhas,
            registrar=None,
        )

        if login_realizado:
            link_usado = link1
            print("Login realizado no primeiro link.")

        else:
            print("Não conseguiu logar no primeiro link. Tentando segundo link...")

            login_realizado = login_no_link(
                driver=driver,
                url=link2,
                email=email_medico,
                senhas=senhas,
                registrar=None,
            )

            if login_realizado:
                link_usado = link2
                print("Login realizado no segundo link.")

        if not login_realizado:
            registrar(
                "login",
                "erro",
                "Não foi possível realizar login em nenhum dos links",
                {
                    "email_medico": email_medico,
                    "link1": link1,
                    "link2": link2,
                },
            )

            salvar_status_prompts(
                email_medico=email_medico,
                mensagem="nao consegui logar",
            )

            return {
                "sucesso": False,
                "status": "login_falhou",
                "mensagem": "Não foi possível realizar login com as senhas informadas.",
                "email_medico": email_medico,
                "quantidade_prompts": 0,
                "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
                "log": str(CAMINHO_LOG_PROMPTS),
            }

        login_confirmado = True

        registrar(
            "login",
            "concluido",
            "Login realizado com sucesso",
            {
                "email_medico": email_medico,
                "link_usado": link_usado,
            },
        )

        # =====================================================
        # EXTRAÇÃO DOS PROMPTS
        # =====================================================

        registrar(
            "extracao",
            "executando",
            "Extraindo prompts dos assistentes",
            {
                "email_medico": email_medico,
                "link_usado": link_usado,
            },
        )

        resultados = extrair_todos_os_prompts(
            driver=driver,
            registrar=registrar,
        )

        prompts = []

        for item in resultados:
            valor = item.get("value")

            if valor and valor.strip():
                prompts.append(valor.strip())

        # =====================================================
        # LOGOU, MAS NÃO EXTRAIU PROMPT
        # =====================================================

        if not prompts:
            registrar(
                "extracao",
                "alerta",
                "Login realizado, mas nenhum prompt foi extraído",
                {
                    "email_medico": email_medico,
                    "link_usado": link_usado,
                    "quantidade_prompts": 0,
                },
            )

            salvar_status_prompts(
                email_medico=email_medico,
                mensagem="consegui logar mas nao extrair o texto",
            )

            return {
                "sucesso": False,
                "status": "sem_prompts",
                "mensagem": "Consegui logar, mas não consegui extrair o texto dos prompts.",
                "email_medico": email_medico,
                "quantidade_prompts": 0,
                "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
                "log": str(CAMINHO_LOG_PROMPTS),
            }

        # =====================================================
        # PROMPTS EXTRAÍDOS COM SUCESSO
        # =====================================================

        prompts_limitados = prompts[:20]

        salvar_resultado_prompts(
            email_medico=email_medico,
            prompts=prompts_limitados,
        )

        registrar(
            "extracao",
            "concluido",
            "Prompts extraídos com sucesso",
            {
                "email_medico": email_medico,
                "link_usado": link_usado,
                "quantidade_prompts": len(prompts_limitados),
            },
        )

        registrar(
            "arquivo",
            "concluido",
            "Arquivo CSV atualizado com os prompts extraídos",
            {
                "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
            },
        )

        registrar(
            "finalizacao",
            "concluido",
            "Extração finalizada",
            {
                "email_medico": email_medico,
                "quantidade_prompts": len(prompts_limitados),
            },
        )

        return {
            "sucesso": True,
            "status": "concluido",
            "mensagem": f"{len(prompts_limitados)} prompt(s) extraído(s) com sucesso.",
            "email_medico": email_medico,
            "quantidade_prompts": len(prompts_limitados),
            "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
            "log": str(CAMINHO_LOG_PROMPTS),
            "prompts": prompts_limitados,
        }

    except Exception as erro:
        registrar(
            "erro",
            "erro",
            "Falha durante a extração de prompts",
            {
                "erro": str(erro),
                "email_medico": email_medico if email_medico else "",
            },
        )

        if login_confirmado:
            mensagem_csv = "consegui logar mas nao extrair o texto"
        else:
            mensagem_csv = "nao consegui logar"

        salvar_status_prompts(
            email_medico=email_medico if email_medico else "",
            mensagem=mensagem_csv,
        )

        return {
            "sucesso": False,
            "status": "erro",
            "mensagem": str(erro),
            "email_medico": email_medico if email_medico else "",
            "quantidade_prompts": 0,
            "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
            "log": str(CAMINHO_LOG_PROMPTS),
        }

    finally:
        if driver:
            registrar(
                "navegador",
                "concluido",
                "Fechando navegador",
                {
                    "email_medico": email_medico if email_medico else "",
                },
            )

            driver.quit()