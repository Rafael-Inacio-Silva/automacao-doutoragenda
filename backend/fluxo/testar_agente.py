import os
import time
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from backend.acoes_acesso.iniciar_navegador import iniciar_chrome
from backend.acoes_acesso.abrir_doutoriagenda import abrir_doutoriagenda
from backend.acoes_acesso.login import (
    preencher_login,
    preencher_senha,
    clicar_entrar,
    esperar_pos_login,
)
from backend.acoes_acesso.clicar_iniciais import clicar_elemento_iniciais

from backend.acoes_menu.clicar_trocar_tenant import clicar_trocar_tenant
from backend.acoes_menu.clicar_gerenciar_agente import clicar_opcao_gerenciar_agentes

from backend.acoes_menu_trocar_tenant.clicar_campo_selecione_tenant_trocar import (
    clicar_campo_selecione_tenant_trocar,
)
from backend.acoes_menu_trocar_tenant.inserir_id_medico import inserir_id_medico
from backend.acoes_menu_trocar_tenant.extrator_tenant_parecido import (
    extrator_tenant_parecido,
)
from backend.acoes_menu_trocar_tenant.clicar_primeiro_tenant import clicar_primeiro_tenant
from backend.acoes_menu_trocar_tenant.clicar_botao_trocar_tenant import (
    clicar_botao_trocar_tenant,
)

from backend.acoes_menu_gerenciar_agentes.clicar_visualizar_agente import (
    clicar_visualizar_agente,
)
from backend.acoes_menu_gerenciar_agentes.extrair_valor_sumarizacao_contexto import (
    extrair_valor_sumarizacao_contexto,
)
from backend.acoes_menu_gerenciar_agentes.clicar_aba_conversa import (
    clicar_aba_conversa,
)
from backend.acoes_menu_gerenciar_agentes.extrair_estagios_conversa import (
    extrair_estagios_conversa,
)

from backend.regras_qa.regras_obrigatorias import (
    validar_tenant_igual_exato,
    validar_sumarizacao_contexto_false,
    validar_estagios_obrigatorios,
    validar_agendamento_estagio_3_llm,
)

from backend.regras_qa.relatorio_qa import (
    preparar_arquivos_resultado,
    adicionar_evento_log,
    gerar_relatorio_txt,
    gerar_relatorio_erro_txt,
    obter_caminho_log_json,
)


# ============================================================
# CAMINHOS
# ============================================================

CAMINHO_RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_BACKEND = Path(__file__).resolve().parents[1]

CAMINHO_ENV_RAIZ = CAMINHO_RAIZ_PROJETO / ".env"
CAMINHO_ENV_BACKEND = CAMINHO_BACKEND / ".env"

if CAMINHO_ENV_RAIZ.exists():
    CAMINHO_ENV = CAMINHO_ENV_RAIZ
else:
    CAMINHO_ENV = CAMINHO_ENV_BACKEND

load_dotenv(CAMINHO_ENV, override=True)

CAMINHO_RESULTADO_QA_LOTE = CAMINHO_RAIZ_PROJETO / "resultado_qa_lote.txt"


# ============================================================
# FUNÇÕES AUXILIARES — ENTRADA DO FRONTEND
# ============================================================

def normalizar_tenants_qa(tenants_texto):
    """
    Recebe do frontend:
    - uma string com um tenant;
    - uma string com vários tenants, um por linha;
    - ou uma lista de tenants.

    Exemplo:
    #586 - Dr. Raphael Palomares Jacobs
    #267 - Dra. Maria Teste
    #199 - Dr. Mike Cardoso

    Retorna uma lista limpa.
    """

    if tenants_texto is None:
        return []

    if isinstance(tenants_texto, list):
        linhas = tenants_texto
    else:
        linhas = str(tenants_texto).splitlines()

    tenants = []

    for linha in linhas:
        tenant = str(linha).strip()

        if not tenant:
            continue

        # Se vier "586 - Dr. Nome", transforma em "#586 - Dr. Nome"
        if not tenant.startswith("#"):
            tenant = f"#{tenant}"

        tenants.append(tenant)

    return tenants


def obter_status_geral_qa(resultado):
    """
    Define o status geral do teste QA de um tenant.
    """

    if not isinstance(resultado, dict):
        return "erro"

    if resultado.get("status") == "erro":
        return "erro"

    regras = resultado.get("resultado_qa", [])

    if not regras:
        return "sem_regras"

    for regra in regras:
        if regra.get("status") == "reprovado":
            return "reprovado"

    return "aprovado"


def gerar_relatorio_lote_qa(resultados):
    """
    Gera um relatório TXT consolidado com todos os tenants testados.
    Esse arquivo é o que o frontend vai baixar no botão de relatório QA.
    """

    linhas = []

    linhas.append("RELATÓRIO DE TESTE QA — LOTE")
    linhas.append("=" * 80)
    linhas.append(f"Data de execução: {datetime.now().isoformat(timespec='seconds')}")
    linhas.append(f"Quantidade de tenants testados: {len(resultados)}")
    linhas.append("=" * 80)
    linhas.append("")

    for indice, resultado in enumerate(resultados, start=1):
        tenant = resultado.get("tenant_teste", "")
        status_geral = obter_status_geral_qa(resultado)
        mensagem = resultado.get("mensagem", "")

        linhas.append(f"{indice}. TENANT: {tenant}")
        linhas.append("-" * 80)
        linhas.append(f"Status geral: {status_geral}")
        linhas.append(f"Mensagem: {mensagem}")
        linhas.append("")

        regras = resultado.get("resultado_qa", [])

        if not regras:
            linhas.append("Nenhuma regra foi executada.")
            linhas.append("")
            linhas.append("=" * 80)
            linhas.append("")
            continue

        for regra in regras:
            linhas.append(f"Regra: {regra.get('regra', '')}")
            linhas.append(f"Status: {regra.get('status', '')}")
            linhas.append(f"Esperado: {regra.get('esperado', '')}")
            linhas.append(f"Encontrado: {regra.get('encontrado', '')}")
            linhas.append(f"Mensagem: {regra.get('mensagem', '')}")
            linhas.append("")

        linhas.append("=" * 80)
        linhas.append("")

    with open(CAMINHO_RESULTADO_QA_LOTE, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))

    return str(CAMINHO_RESULTADO_QA_LOTE)


# ============================================================
# FLUXO UNITÁRIO — TESTA 1 TENANT
# ============================================================

def fluxo_testar_agente(
    tenant_teste: str,
    log=None,
    limpar_arquivos: bool = False,
    indice: int = 1,
    total: int = 1,
    fechar_navegador: bool = True,
):
    driver = None
    eventos = []
    resultados_regras = []

    tenant_teste = str(tenant_teste).strip()

    if not tenant_teste:
        raise ValueError("Tenant de teste não informado.")

    if not tenant_teste.startswith("#"):
        tenant_teste = f"#{tenant_teste}"

    if limpar_arquivos:
        preparar_arquivos_resultado()

    def registrar(etapa, status, mensagem, dados=None):
        """
        Registra evento:
        - no log JSON do QA;
        - no terminal;
        - no stream do frontend, se log for informado.
        """

        dados = dados or {}

        dados_base = {
            "tenant_teste": tenant_teste,
            "indice": indice,
            "total": total,
        }

        dados_final = {
            **dados_base,
            **dados,
        }

        adicionar_evento_log(
            eventos,
            etapa=etapa,
            status=status,
            mensagem=mensagem,
            dados=dados_final,
        )

        evento_front = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "fluxo": "testar_agente_qa",
            "etapa": etapa,
            "status": status,
            "mensagem": mensagem,
            "dados": dados_final,
        }

        print(evento_front)

        if log:
            log(evento_front)

    try:
        registrar(
            etapa="inicio",
            status="executando",
            mensagem="Iniciando fluxo de teste QA do agente.",
        )

        login_sistema = os.getenv("LOGIN_EMAIL")
        senha_sistema = os.getenv("LOGIN_SENHA")

        if not login_sistema or not senha_sistema:
            mensagem = "LOGIN_EMAIL ou LOGIN_SENHA não encontrados no .env"

            registrar(
                etapa="validar_env",
                status="erro",
                mensagem=mensagem,
                dados={
                    "env_verificado": str(CAMINHO_ENV),
                },
            )

            caminho_relatorio = gerar_relatorio_erro_txt(
                mensagem_erro=mensagem,
                id_medico_teste=tenant_teste,
            )

            return {
                "status": "erro",
                "teste": "login_env",
                "tenant_teste": tenant_teste,
                "mensagem": mensagem,
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        registrar(
            etapa="login_env",
            status="executado",
            mensagem="Credenciais encontradas no .env.",
            dados={
                "env_carregado": str(CAMINHO_ENV),
            },
        )

        driver = iniciar_chrome()

        registrar(
            etapa="abrir_navegador",
            status="executado",
            mensagem="Navegador iniciado com sucesso.",
        )

        abrir_doutoriagenda(driver)

        registrar(
            etapa="abrir_sistema",
            status="executado",
            mensagem="Sistema DrIA aberto com sucesso.",
        )

        preencher_login(driver, login_sistema)
        preencher_senha(driver, senha_sistema)
        clicar_entrar(driver)
        esperar_pos_login(driver)

        registrar(
            etapa="login",
            status="executado",
            mensagem="Login realizado com sucesso.",
        )

        # ============================================================
        # NAVEGAÇÃO — ABRIR MENU E ACESSAR TROCA DE TENANT
        # ============================================================

        clicar_elemento_iniciais(driver)
        clicar_trocar_tenant(driver)
        clicar_campo_selecione_tenant_trocar(driver)

        registrar(
            etapa="abrir_troca_tenant",
            status="executado",
            mensagem="Área de troca de tenant aberta com sucesso.",
        )

        inserir_id_medico(driver, tenant_teste)

        registrar(
            etapa="inserir_id_medico",
            status="executado",
            mensagem="ID do médico inserido no campo de busca.",
        )

        resultado_extracao = extrator_tenant_parecido(driver)

        registrar(
            etapa="extrair_tenants",
            status="executado",
            mensagem="Resultado da busca de tenants extraído com sucesso.",
            dados={
                "resultado_extracao": resultado_extracao,
            },
        )

        # ============================================================
        # REGRA 1 — VALIDAR TENANT 100% IGUAL
        # ============================================================

        resultado_regra_tenant = validar_tenant_igual_exato(
            resultado_extracao,
            tenant_teste,
        )

        resultados_regras.append(resultado_regra_tenant)

        registrar(
            etapa="regra_1",
            status="executado",
            mensagem="Regra 1 executada: validação de tenant igual/exato.",
            dados=resultado_regra_tenant,
        )

        status_regra_1 = resultado_regra_tenant.get("status")

        if status_regra_1 != "aprovado":
            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=tenant_teste,
                resultados_regras=resultados_regras,
            )

            registrar(
                etapa="fim",
                status="executado",
                mensagem="Fluxo finalizado na Regra 1.",
                dados={
                    "relatorio_txt": caminho_relatorio,
                },
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": tenant_teste,
                "mensagem": "Regra 1 reprovada. Fluxo encerrado.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        # ============================================================
        # PÓS-REGRA 1 — SELECIONAR TENANT E TROCAR
        # ============================================================

        registrar(
            etapa="regra_1_aprovada",
            status="executado",
            mensagem="Regra 1 aprovada. Prosseguindo para troca de tenant.",
        )

        clicou_tenant = clicar_primeiro_tenant(driver)

        if not clicou_tenant:
            resultado_clique_tenant = {
                "regra": "Navegação — Clique no tenant aprovado",
                "status": "reprovado",
                "esperado": tenant_teste,
                "encontrado": resultado_extracao,
                "mensagem": "Tenant foi aprovado na comparação, mas não foi possível clicar nele.",
            }

            resultados_regras.append(resultado_clique_tenant)

            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=tenant_teste,
                resultados_regras=resultados_regras,
            )

            registrar(
                etapa="fim",
                status="executado",
                mensagem="Tenant aprovado, mas falhou ao clicar.",
                dados={
                    "relatorio_txt": caminho_relatorio,
                },
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": tenant_teste,
                "mensagem": "Tenant aprovado, mas falhou ao clicar.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        registrar(
            etapa="clicar_tenant",
            status="executado",
            mensagem="Tenant aprovado selecionado com sucesso.",
        )

        clicou_botao_trocar = clicar_botao_trocar_tenant(driver)

        if not clicou_botao_trocar:
            resultado_botao_trocar = {
                "regra": "Navegação — Clique no botão Trocar",
                "status": "reprovado",
                "esperado": "Botão Trocar clicável após selecionar o tenant.",
                "encontrado": "Botão Trocar não foi clicado.",
                "mensagem": "Tenant foi selecionado, mas não foi possível clicar no botão Trocar.",
            }

            resultados_regras.append(resultado_botao_trocar)

            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=tenant_teste,
                resultados_regras=resultados_regras,
            )

            registrar(
                etapa="fim",
                status="executado",
                mensagem="Tenant selecionado, mas falhou ao clicar no botão Trocar.",
                dados={
                    "relatorio_txt": caminho_relatorio,
                },
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": tenant_teste,
                "mensagem": "Tenant selecionado, mas falhou ao clicar no botão Trocar.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        registrar(
            etapa="clicar_botao_trocar",
            status="executado",
            mensagem="Botão Trocar clicado com sucesso.",
        )

        # ============================================================
        # ACESSAR GERENCIAR AGENTES
        # ============================================================

        clicar_elemento_iniciais(driver)

        registrar(
            etapa="clicar_iniciais_pos_troca",
            status="executado",
            mensagem="Menu das iniciais aberto com sucesso após troca de tenant.",
        )

        clicou_gerenciar_agentes = clicar_opcao_gerenciar_agentes(driver)

        if not clicou_gerenciar_agentes:
            resultado_gerenciar_agentes = {
                "regra": "Navegação — Acessar Gerenciar Agentes",
                "status": "reprovado",
                "esperado": "Acessar Gerenciar Agentes pelo menu das iniciais.",
                "encontrado": "Não foi possível clicar em Gerenciar Agentes.",
                "mensagem": "Tenant foi trocado, mas não foi possível acessar Gerenciar Agentes.",
            }

            resultados_regras.append(resultado_gerenciar_agentes)

            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=tenant_teste,
                resultados_regras=resultados_regras,
            )

            registrar(
                etapa="fim",
                status="executado",
                mensagem="Tenant trocado, mas falhou ao acessar Gerenciar Agentes.",
                dados={
                    "relatorio_txt": caminho_relatorio,
                },
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": tenant_teste,
                "mensagem": "Tenant trocado, mas falhou ao acessar Gerenciar Agentes.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        registrar(
            etapa="clicar_gerenciar_agentes",
            status="executado",
            mensagem="Gerenciar Agentes acessado com sucesso.",
        )

        clicou_visualizar_agente = clicar_visualizar_agente(driver)

        if not clicou_visualizar_agente:
            resultado_visualizar_agente = {
                "regra": "Navegação — Visualizar Agente",
                "status": "reprovado",
                "esperado": "Botão Visualizar Agente disponível e clicável.",
                "encontrado": "Não foi possível clicar no botão Visualizar Agente.",
                "mensagem": "Gerenciar Agentes foi acessado, mas não foi possível visualizar o agente.",
            }

            resultados_regras.append(resultado_visualizar_agente)

            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=tenant_teste,
                resultados_regras=resultados_regras,
            )

            registrar(
                etapa="fim",
                status="executado",
                mensagem="Gerenciar Agentes acessado, mas falhou ao clicar em Visualizar Agente.",
                dados={
                    "relatorio_txt": caminho_relatorio,
                },
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": tenant_teste,
                "mensagem": "Gerenciar Agentes acessado, mas falhou ao clicar em Visualizar Agente.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        registrar(
            etapa="clicar_visualizar_agente",
            status="executado",
            mensagem="Botão Visualizar Agente clicado com sucesso.",
        )

        # ============================================================
        # REGRA 2 — SUMARIZAÇÃO DE CONTEXTO DEVE ESTAR FALSE
        # ============================================================

        time.sleep(2)

        dados_sumarizacao = extrair_valor_sumarizacao_contexto(driver)

        registrar(
            etapa="extrair_sumarizacao_contexto",
            status="executado",
            mensagem="Extração do campo Sumarização de Contexto executada.",
            dados=dados_sumarizacao,
        )

        valor_sumarizacao = dados_sumarizacao.get("valor")

        resultado_regra_sumarizacao = validar_sumarizacao_contexto_false(
            valor_sumarizacao
        )

        resultado_regra_sumarizacao["dados_extracao"] = dados_sumarizacao

        resultados_regras.append(resultado_regra_sumarizacao)

        registrar(
            etapa="regra_2",
            status="executado",
            mensagem="Regra 2 executada: Sumarização de Contexto deve estar false.",
            dados=resultado_regra_sumarizacao,
        )

        # ============================================================
        # REGRA 3 — ESTÁGIOS OBRIGATÓRIOS
        # ============================================================

        clicou_aba_conversa = clicar_aba_conversa(driver)

        if not clicou_aba_conversa:
            resultado_aba_conversa = {
                "regra": "Navegação — Clicar na aba Conversa",
                "status": "reprovado",
                "esperado": "Aba Conversa disponível e clicável.",
                "encontrado": "Aba Conversa não foi clicada.",
                "mensagem": "Não foi possível clicar na aba Conversa para executar a Regra 3.",
            }

            resultados_regras.append(resultado_aba_conversa)

            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=tenant_teste,
                resultados_regras=resultados_regras,
            )

            registrar(
                etapa="fim",
                status="executado",
                mensagem="Falhou ao clicar na aba Conversa.",
                dados={
                    "relatorio_txt": caminho_relatorio,
                },
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": tenant_teste,
                "mensagem": "Falhou ao clicar na aba Conversa.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        registrar(
            etapa="clicar_aba_conversa",
            status="executado",
            mensagem="Aba Conversa clicada com sucesso.",
        )

        dados_estagios = extrair_estagios_conversa(driver)

        registrar(
            etapa="extrair_estagios_conversa",
            status=dados_estagios.get("status", "executado"),
            mensagem="Extração dos estágios da aba Conversa executada.",
            dados=dados_estagios,
        )

        resultado_regra_estagios = validar_estagios_obrigatorios(
            dados_estagios
        )

        resultado_regra_estagios["dados_extracao"] = dados_estagios

        resultados_regras.append(resultado_regra_estagios)

        registrar(
            etapa="regra_3",
            status="executado",
            mensagem="Regra 3 executada: validação dos estágios obrigatórios.",
            dados=resultado_regra_estagios,
        )

        # ============================================================
        # REGRA 4 — VALIDAÇÃO LLM DO ESTÁGIO 3 AGENDAMENTO
        # ============================================================

        resultado_regra_agendamento_llm = validar_agendamento_estagio_3_llm(
            dados_estagios
        )

        resultados_regras.append(resultado_regra_agendamento_llm)

        registrar(
            etapa="regra_4",
            status="executado",
            mensagem="Regra 4 executada: validação LLM do Estágio 3 Agendamento.",
            dados=resultado_regra_agendamento_llm,
        )

        # ============================================================
        # FINALIZAR RELATÓRIO INDIVIDUAL
        # ============================================================

        caminho_relatorio = gerar_relatorio_txt(
            status_geral="executado",
            id_medico_teste=tenant_teste,
            resultados_regras=resultados_regras,
        )

        registrar(
            etapa="relatorio",
            status="executado",
            mensagem="Relatório TXT individual gerado com sucesso.",
            dados={
                "relatorio_txt": caminho_relatorio,
            },
        )

        registrar(
            etapa="fim",
            status="executado",
            mensagem="Fluxo de teste QA finalizado após execução das regras obrigatórias.",
        )

        return {
            "status": "executado",
            "teste": "testar_agente_qa",
            "tenant_teste": tenant_teste,
            "mensagem": "Fluxo QA executado. Regra 1, Regra 2, Regra 3 e Regra 4 foram validadas.",
            "resultado_qa": resultados_regras,
            "relatorio_txt": caminho_relatorio,
            "log_json": obter_caminho_log_json(),
        }

    except Exception as erro:
        mensagem_erro = str(erro)

        registrar(
            etapa="erro",
            status="erro",
            mensagem="Erro no fluxo testar agente.",
            dados={
                "erro": mensagem_erro,
            },
        )

        caminho_relatorio = gerar_relatorio_erro_txt(
            mensagem_erro=mensagem_erro,
            id_medico_teste=tenant_teste,
        )

        return {
            "status": "erro",
            "teste": "fluxo_testar_agente",
            "tenant_teste": tenant_teste,
            "mensagem": mensagem_erro,
            "resultado_qa": resultados_regras,
            "relatorio_txt": caminho_relatorio,
            "log_json": obter_caminho_log_json(),
        }

    finally:
        if driver and fechar_navegador:
            try:
                driver.quit()
            except Exception:
                pass


# ============================================================
# FLUXO EM LOTE — PRONTO PARA O FRONTEND
# ============================================================

def fluxo_testar_agentes(
    tenants_texto,
    log=None,
    limpar_arquivos: bool = False,
):
    """
    Função preparada para o frontend.

    Recebe uma string com um ou vários tenants:

    #586 - Dr. Raphael Palomares Jacobs
    #267 - Dra. Maria Teste
    #199 - Dr. Mike Cardoso

    Executa um por vez e retorna resultado consolidado.
    """

    if limpar_arquivos:
        preparar_arquivos_resultado()

    tenants = normalizar_tenants_qa(tenants_texto)

    if not tenants:
        caminho_relatorio = gerar_relatorio_lote_qa([])

        return {
            "sucesso": False,
            "status": "erro",
            "teste": "testar_agentes_qa",
            "mensagem": "Nenhum tenant foi informado.",
            "quantidade": 0,
            "aprovados": 0,
            "reprovados": 0,
            "erros": 1,
            "resultados": [],
            "relatorio_txt": caminho_relatorio,
            "log_json": obter_caminho_log_json(),
        }

    resultados = []
    total = len(tenants)

    for indice, tenant_teste in enumerate(tenants, start=1):
        evento_inicio_item = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "fluxo": "testar_agentes_qa",
            "etapa": "inicio_item",
            "status": "executando",
            "mensagem": f"Iniciando teste QA {indice}/{total}.",
            "dados": {
                "tenant_teste": tenant_teste,
                "indice": indice,
                "total": total,
            },
        }

        print(evento_inicio_item)

        if log:
            log(evento_inicio_item)

        resultado = fluxo_testar_agente(
            tenant_teste=tenant_teste,
            log=log,
            limpar_arquivos=False,
            indice=indice,
            total=total,
            fechar_navegador=True,
        )

        resultados.append(resultado)

        evento_fim_item = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "fluxo": "testar_agentes_qa",
            "etapa": "fim_item",
            "status": "executado",
            "mensagem": f"Teste QA {indice}/{total} finalizado.",
            "dados": {
                "tenant_teste": tenant_teste,
                "indice": indice,
                "total": total,
                "status_geral": obter_status_geral_qa(resultado),
            },
        }

        print(evento_fim_item)

        if log:
            log(evento_fim_item)

    caminho_relatorio_lote = gerar_relatorio_lote_qa(resultados)

    aprovados = 0
    reprovados = 0
    erros = 0

    for resultado in resultados:
        status_geral = obter_status_geral_qa(resultado)

        if status_geral == "aprovado":
            aprovados += 1
        elif status_geral == "reprovado":
            reprovados += 1
        else:
            erros += 1

    resultado_final = {
        "sucesso": erros == 0 and reprovados == 0,
        "status": "executado",
        "teste": "testar_agentes_qa",
        "mensagem": "Fluxo QA em lote executado.",
        "quantidade": total,
        "aprovados": aprovados,
        "reprovados": reprovados,
        "erros": erros,
        "resultados": resultados,
        "relatorio_txt": caminho_relatorio_lote,
        "log_json": obter_caminho_log_json(),
    }

    evento_final = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "fluxo": "testar_agentes_qa",
        "etapa": "finalizacao_lote",
        "status": "executado",
        "mensagem": "Fluxo QA em lote finalizado.",
        "dados": {
            "quantidade": total,
            "aprovados": aprovados,
            "reprovados": reprovados,
            "erros": erros,
            "relatorio_txt": caminho_relatorio_lote,
            "log_json": obter_caminho_log_json(),
        },
    }

    print(evento_final)

    if log:
        log(evento_final)

    return resultado_final


# ============================================================
# TESTE LOCAL
# ============================================================

if __name__ == "__main__":
    entrada = """
#586 - Dr. Raphael Palomares Jacobs
"""

    resultado = fluxo_testar_agentes(
        tenants_texto=entrada,
        limpar_arquivos=True,
    )

    print(json.dumps(resultado, ensure_ascii=False, indent=2))