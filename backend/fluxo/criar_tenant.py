import os
import csv
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from backend.acoes_acesso.iniciar_navegador import iniciar_chrome
from backend.acoes_acesso.abrir_doutoriagenda import abrir_doutoriagenda
from backend.acoes_acesso.login import preencher_login, preencher_senha, clicar_entrar, esperar_pos_login
from backend.acoes_acesso.clicar_iniciais import clicar_elemento_iniciais
from backend.acoes_menu.clicar_trocar_tenant import clicar_trocar_tenant
from backend.acoes_menu_trocar_tenant.clicar_campo_selecione_tenant_trocar import clicar_campo_selecione_tenant_trocar
from backend.acoes_menu_trocar_tenant.inserir_id_medico import inserir_id_medico
from backend.acoes_menu_trocar_tenant.extrator_tenant_parecido import extrator_tenant_parecido
from backend.acoes_tenant.analisador_tenant import analisar_tenant
from backend.acoes_tenant.fechar_caixa_busca_tenant import fechar_modal_tenant
from backend.acoes_menu.clicar_gerenciar_tenant import clicar_opcao_gerencia_tenant
from backend.acoes_menu_gerenciar_tenant.criar_novo_tenant import clicar_botao_tenant
from backend.acoes_menu_gerenciar_tenant.inserir_nome_novo_tenant import inserir_id_e_nome_medico, clicar_criar_tenant


CAMINHO_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(CAMINHO_ENV)

CAMINHO_RAIZ = Path(__file__).resolve().parents[1]
CAMINHO_RESULTADO_TENANT = CAMINHO_RAIZ / "resultado_tenant.csv"
CAMINHO_LOG_TENANT = CAMINHO_RAIZ / "log_tenant.json"


def limpar_arquivo_resultado_tenant():
    """
    Cria ou limpa o arquivo CSV de resultado do tenant.
    """
    with open(CAMINHO_RESULTADO_TENANT, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow([
            "id_medico",
            "nome_medico",
            "status",
            "mensagem",
            "tenant",
            "data_execucao",
        ])


def limpar_arquivo_log_tenant():
    """
    Cria ou limpa o arquivo JSON de log do tenant.
    """
    with open(CAMINHO_LOG_TENANT, "w", encoding="utf-8") as arquivo:
        json.dump([], arquivo, ensure_ascii=False, indent=2)


def salvar_resultado_tenant(id_medico, nome_medico, status, mensagem, tenant=""):
    """
    Salva uma linha no CSV de resultado da criação de tenant.
    """
    if not CAMINHO_RESULTADO_TENANT.exists():
        limpar_arquivo_resultado_tenant()

    with open(CAMINHO_RESULTADO_TENANT, "a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow([
            id_medico,
            nome_medico,
            status,
            mensagem,
            tenant,
            datetime.now().isoformat(timespec="seconds"),
        ])


def salvar_log_tenant(evento):
    """
    Salva cada evento da automação no arquivo JSON de log do tenant.
    """
    if not CAMINHO_LOG_TENANT.exists():
        limpar_arquivo_log_tenant()

    try:
        with open(CAMINHO_LOG_TENANT, "r", encoding="utf-8") as arquivo:
            logs = json.load(arquivo)
    except Exception:
        logs = []

    logs.append(evento)

    with open(CAMINHO_LOG_TENANT, "w", encoding="utf-8") as arquivo:
        json.dump(logs, arquivo, ensure_ascii=False, indent=2)


def fluxo_criar_tenant(id_medico: str, nome_medico: str, log=None):
    driver = None

    def registrar(etapa, status, mensagem, dados=None):
        evento = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "fluxo": "criar_tenant",
            "etapa": etapa,
            "status": status,
            "mensagem": mensagem,
            "dados": dados or {},
        }

        print(evento)

        salvar_log_tenant(evento)

        if log:
            log(evento)

    try:
        id_medico = id_medico.strip()
        nome_medico = nome_medico.strip()

        if not id_medico:
            raise ValueError("ID do médico não informado.")

        if not nome_medico:
            raise ValueError("Nome do médico não informado.")

        if not id_medico.startswith("#"):
            id_medico = f"#{id_medico}"

        login_usuario = os.getenv("LOGIN_EMAIL")
        senha_usuario = os.getenv("LOGIN_SENHA")

        if not login_usuario or not senha_usuario:
            raise ValueError("LOGIN_EMAIL ou LOGIN_SENHA não encontrados no arquivo .env")

        registrar("inicio", "executando", "Iniciando automação")

        registrar("navegador", "executando", "Abrindo navegador")
        driver = iniciar_chrome()
        registrar("navegador", "concluido", "Navegador iniciado")

        registrar("acesso", "executando", "Acessando DoutorAgenda")
        abrir_doutoriagenda(driver)
        registrar("acesso", "concluido", "Sistema acessado")

        registrar("login", "executando", "Realizando login")
        preencher_login(driver, login_usuario)
        preencher_senha(driver, senha_usuario)
        clicar_entrar(driver)
        esperar_pos_login(driver)
        registrar("login", "concluido", "Login realizado com sucesso")

        registrar("busca_tenant", "executando", "Buscando tenant informado", {
            "id_medico": id_medico
        })

        clicar_elemento_iniciais(driver)
        clicar_trocar_tenant(driver)
        clicar_campo_selecione_tenant_trocar(driver)
        inserir_id_medico(driver, id_medico)

        resultado = extrator_tenant_parecido(driver)
        existe_tenant, tenant_encontrado = analisar_tenant(resultado, id_medico)

        if existe_tenant:
            registrar("busca_tenant", "alerta", "Tenant já existe", {
                "tenant_encontrado": tenant_encontrado
            })

            salvar_resultado_tenant(
                id_medico=id_medico,
                nome_medico=nome_medico,
                status="tenant_existente",
                mensagem=f"Tenant já existe: {tenant_encontrado}",
                tenant=tenant_encontrado,
            )

            return {
                "sucesso": False,
                "status": "tenant_existente",
                "mensagem": f"Tenant já existe: {tenant_encontrado}",
                "tenant": tenant_encontrado,
            }

        registrar("busca_tenant", "concluido", "Tenant não encontrado")

        registrar("criacao_tenant", "executando", "Criando novo tenant", {
            "id_medico": id_medico,
            "nome_medico": nome_medico,
        })

        fechar_modal_tenant(driver)
        clicar_elemento_iniciais(driver)
        clicar_opcao_gerencia_tenant(driver)
        clicar_botao_tenant(driver)
        inserir_id_e_nome_medico(driver, id_medico, nome_medico)
        clicar_criar_tenant()

        registrar("criacao_tenant", "concluido", "Tenant criado com sucesso")

        registrar("finalizacao", "concluido", "Automação finalizada")

        salvar_resultado_tenant(
            id_medico=id_medico,
            nome_medico=nome_medico,
            status="criado",
            mensagem="Tenant criado com sucesso.",
            tenant=f"{id_medico} - {nome_medico}",
        )

        return {
            "sucesso": True,
            "status": "concluido",
            "mensagem": "Tenant criado com sucesso.",
            "tenant": f"{id_medico} - {nome_medico}",
        }

    except Exception as erro:
        registrar("erro", "erro", "Falha durante a automação", {
            "erro": str(erro)
        })

        salvar_resultado_tenant(
            id_medico=id_medico if "id_medico" in locals() else "",
            nome_medico=nome_medico if "nome_medico" in locals() else "",
            status="erro",
            mensagem=str(erro),
            tenant="",
        )

        return {
            "sucesso": False,
            "status": "erro",
            "mensagem": str(erro),
        }

    finally:
        if driver:
            registrar("navegador", "concluido", "Fechando navegador")
            driver.quit()