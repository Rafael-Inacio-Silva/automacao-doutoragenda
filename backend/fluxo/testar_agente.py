import os
import time
from pathlib import Path
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


CAMINHO_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(CAMINHO_ENV)

ID_MEDICO_TESTE = "#586 - Dr. Raphael Palomares Jacobs"


def fluxo_testar_agente():
    driver = None
    eventos = []
    resultados_regras = []

    preparar_arquivos_resultado()

    try:
        adicionar_evento_log(
            eventos,
            etapa="inicio",
            status="executando",
            mensagem="Iniciando fluxo de teste QA do agente.",
            dados={
                "tenant_teste": ID_MEDICO_TESTE,
            },
        )

        login_sistema = os.getenv("LOGIN_EMAIL")
        senha_sistema = os.getenv("LOGIN_SENHA")

        if not login_sistema or not senha_sistema:
            mensagem = "LOGIN_EMAIL ou LOGIN_SENHA não encontrados no .env"

            adicionar_evento_log(
                eventos,
                etapa="validar_env",
                status="erro",
                mensagem=mensagem,
            )

            caminho_relatorio = gerar_relatorio_erro_txt(
                mensagem_erro=mensagem,
                id_medico_teste=ID_MEDICO_TESTE,
            )

            return {
                "status": "erro",
                "teste": "login_env",
                "mensagem": mensagem,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        adicionar_evento_log(
            eventos,
            etapa="login_env",
            status="executado",
            mensagem="Credenciais encontradas no .env.",
        )

        driver = iniciar_chrome()

        adicionar_evento_log(
            eventos,
            etapa="abrir_navegador",
            status="executado",
            mensagem="Navegador iniciado com sucesso.",
        )

        abrir_doutoriagenda(driver)

        adicionar_evento_log(
            eventos,
            etapa="abrir_sistema",
            status="executado",
            mensagem="Sistema DrIA aberto com sucesso.",
        )

        preencher_login(driver, login_sistema)
        preencher_senha(driver, senha_sistema)
        clicar_entrar(driver)
        esperar_pos_login(driver)

        adicionar_evento_log(
            eventos,
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

        adicionar_evento_log(
            eventos,
            etapa="abrir_troca_tenant",
            status="executado",
            mensagem="Área de troca de tenant aberta com sucesso.",
        )

        inserir_id_medico(driver, ID_MEDICO_TESTE)

        adicionar_evento_log(
            eventos,
            etapa="inserir_id_medico",
            status="executado",
            mensagem="ID do médico inserido no campo de busca.",
            dados={
                "tenant_teste": ID_MEDICO_TESTE,
            },
        )

        resultado_extracao = extrator_tenant_parecido(driver)

        adicionar_evento_log(
            eventos,
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
            ID_MEDICO_TESTE,
        )

        resultados_regras.append(resultado_regra_tenant)

        adicionar_evento_log(
            eventos,
            etapa="regra_1",
            status="executado",
            mensagem="Regra 1 executada: validação de tenant igual/exato.",
            dados=resultado_regra_tenant,
        )

        status_regra_1 = resultado_regra_tenant.get("status")

        if status_regra_1 != "aprovado":
            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=ID_MEDICO_TESTE,
                resultados_regras=resultados_regras,
            )

            adicionar_evento_log(
                eventos,
                etapa="fim",
                status="executado",
                mensagem="Fluxo finalizado na Regra 1.",
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": ID_MEDICO_TESTE,
                "mensagem": "Regra 1 reprovada. Fluxo encerrado.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        # ============================================================
        # PÓS-REGRA 1 — SELECIONAR TENANT E TROCAR
        # ============================================================

        adicionar_evento_log(
            eventos,
            etapa="regra_1_aprovada",
            status="executado",
            mensagem="Regra 1 aprovada. Prosseguindo para troca de tenant.",
            dados={
                "tenant_teste": ID_MEDICO_TESTE,
            },
        )

        clicou_tenant = clicar_primeiro_tenant(driver)

        if not clicou_tenant:
            resultado_clique_tenant = {
                "regra": "Navegação — Clique no tenant aprovado",
                "status": "reprovado",
                "esperado": ID_MEDICO_TESTE,
                "encontrado": resultado_extracao,
                "mensagem": "Tenant foi aprovado na comparação, mas não foi possível clicar nele.",
            }

            resultados_regras.append(resultado_clique_tenant)

            caminho_relatorio = gerar_relatorio_txt(
                status_geral="executado",
                id_medico_teste=ID_MEDICO_TESTE,
                resultados_regras=resultados_regras,
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": ID_MEDICO_TESTE,
                "mensagem": "Tenant aprovado, mas falhou ao clicar.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        adicionar_evento_log(
            eventos,
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
                id_medico_teste=ID_MEDICO_TESTE,
                resultados_regras=resultados_regras,
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": ID_MEDICO_TESTE,
                "mensagem": "Tenant selecionado, mas falhou ao clicar no botão Trocar.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        adicionar_evento_log(
            eventos,
            etapa="clicar_botao_trocar",
            status="executado",
            mensagem="Botão Trocar clicado com sucesso.",
        )

        # ============================================================
        # ACESSAR GERENCIAR AGENTES
        # ============================================================

        clicar_elemento_iniciais(driver)

        adicionar_evento_log(
            eventos,
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
                id_medico_teste=ID_MEDICO_TESTE,
                resultados_regras=resultados_regras,
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": ID_MEDICO_TESTE,
                "mensagem": "Tenant trocado, mas falhou ao acessar Gerenciar Agentes.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        adicionar_evento_log(
            eventos,
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
                id_medico_teste=ID_MEDICO_TESTE,
                resultados_regras=resultados_regras,
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": ID_MEDICO_TESTE,
                "mensagem": "Gerenciar Agentes acessado, mas falhou ao clicar em Visualizar Agente.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        adicionar_evento_log(
            eventos,
            etapa="clicar_visualizar_agente",
            status="executado",
            mensagem="Botão Visualizar Agente clicado com sucesso.",
        )


        # ============================================================
        # REGRA 2 — SUMARIZAÇÃO DE CONTEXTO DEVE ESTAR FALSE
        # ============================================================
        time.sleep(2)
        dados_sumarizacao = extrair_valor_sumarizacao_contexto(driver)

        adicionar_evento_log(
            eventos,
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

        adicionar_evento_log(
            eventos,
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
                id_medico_teste=ID_MEDICO_TESTE,
                resultados_regras=resultados_regras,
            )

            return {
                "status": "executado",
                "teste": "testar_agente_qa",
                "tenant_teste": ID_MEDICO_TESTE,
                "mensagem": "Falhou ao clicar na aba Conversa.",
                "resultado_qa": resultados_regras,
                "relatorio_txt": caminho_relatorio,
                "log_json": obter_caminho_log_json(),
            }

        adicionar_evento_log(
            eventos,
            etapa="clicar_aba_conversa",
            status="executado",
            mensagem="Aba Conversa clicada com sucesso.",
        )

        dados_estagios = extrair_estagios_conversa(driver)

        adicionar_evento_log(
            eventos,
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

        adicionar_evento_log(
            eventos,
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

        adicionar_evento_log(
         eventos,
         etapa="regra_4",
         status="executado",
         mensagem="Regra 4 executada: validação LLM do Estágio 3 Agendamento.",
         dados=resultado_regra_agendamento_llm,
        )

        # ============================================================
        # FINALIZAR RELATÓRIO COM REGRA 1, REGRA 2 E REGRA 3
        # ============================================================

        caminho_relatorio = gerar_relatorio_txt(
            status_geral="executado",
            id_medico_teste=ID_MEDICO_TESTE,
            resultados_regras=resultados_regras,
        )

        adicionar_evento_log(
            eventos,
            etapa="relatorio",
            status="executado",
            mensagem="Relatório TXT gerado com sucesso com as regras executadas.",
            dados={
                "relatorio_txt": caminho_relatorio,
            },
        )

        adicionar_evento_log(
            eventos,
            etapa="fim",
            status="executado",
            mensagem="Fluxo de teste QA finalizado após execução da Regra 1, Regra 2 e Regra 3.",
        )

        return {
            "status": "executado",
            "teste": "testar_agente_qa",
            "tenant_teste": ID_MEDICO_TESTE,
            "mensagem": "Fluxo QA executado. Regra 1, Regra 2, Regra 3 e Regra 4 foram validadas.",
            "resultado_qa": resultados_regras,
            "relatorio_txt": caminho_relatorio,
            "log_json": obter_caminho_log_json(),
        }

    except Exception as erro:
        mensagem_erro = str(erro)

        adicionar_evento_log(
            eventos,
            etapa="erro",
            status="erro",
            mensagem="Erro no fluxo testar agente.",
            dados={
                "erro": mensagem_erro,
            },
        )

        caminho_relatorio = gerar_relatorio_erro_txt(
            mensagem_erro=mensagem_erro,
            id_medico_teste=ID_MEDICO_TESTE,
        )

        return {
            "status": "erro",
            "teste": "fluxo_testar_agente",
            "mensagem": mensagem_erro,
            "relatorio_txt": caminho_relatorio,
            "log_json": obter_caminho_log_json(),
        }

    finally:
        # Deixe comentado para ver a tela
        # if driver:
        #     driver.quit()
        pass


if __name__ == "__main__":
    resultado = fluxo_testar_agente()
    print(resultado)