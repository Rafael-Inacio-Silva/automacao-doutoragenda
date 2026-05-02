import os
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
from backend.acoes_menu_trocar_tenant.clicar_campo_selecione_tenant_trocar import (
    clicar_campo_selecione_tenant_trocar,
)
from backend.acoes_menu_trocar_tenant.inserir_id_medico import inserir_id_medico
from backend.acoes_menu_trocar_tenant.extrator_tenant_parecido import (
    extrator_tenant_parecido,
)
from backend.regras_qa.regras_obrigatorias import validar_tenant_igual_exato
from backend.regras_qa.relatorio_qa import (
    preparar_arquivos_resultado,
    adicionar_evento_log,
    gerar_relatorio_txt,
    gerar_relatorio_erro_txt,
    obter_caminho_log_json,
)


CAMINHO_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(CAMINHO_ENV)

ID_MEDICO_TESTE = "#93 Dra. Renata Fabiani"


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

        caminho_relatorio = gerar_relatorio_txt(
            status_geral="executado",
            id_medico_teste=ID_MEDICO_TESTE,
            resultados_regras=resultados_regras,
        )

        adicionar_evento_log(
            eventos,
            etapa="relatorio",
            status="executado",
            mensagem="Relatório TXT gerado com sucesso.",
            dados={
                "relatorio_txt": caminho_relatorio,
            },
        )

        adicionar_evento_log(
            eventos,
            etapa="fim",
            status="executado",
            mensagem="Fluxo de teste QA finalizado.",
        )

        return {
            "status": "executado",
            "teste": "testar_agente_qa",
            "tenant_teste": ID_MEDICO_TESTE,
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