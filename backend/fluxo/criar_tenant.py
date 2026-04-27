import os
from pathlib import Path

from dotenv import load_dotenv

from backend.acoes.iniciar_navegador import iniciar_chrome
from backend.acoes.abrir_doutoriagenda import abrir_doutoriagenda
from backend.acoes.login import (
    preencher_login,
    preencher_senha,
    clicar_entrar,
    esperar_pos_login,
)
from backend.acoes.clicar_iniciais import clicar_elemento_iniciais
from backend.acoes.clicar_trocar_tenant import clicar_trocar_tenant
from backend.acoes.clicar_campo_Selecione_tenant_trocar import clicar_campo_Selecione_tenant_trocar
from backend.acoes.inserir_id_medico import inserir_id_medico
from backend.acoes.extrator_tenant_parecido import extrator_tenant_parecido
from backend.acoes.analisador_tenant import analisar_tenant
from backend.acoes.fechar_caixa_busca_tenant import fechar_modal_tenant
from backend.acoes.clicar_gerencia_tenant import clicar_opcao_gerencia_tenant
from backend.acoes.criar_novo_tenant import clicar_botao_tenant
from backend.acoes.inserir_nome_novo_tenant import (
    inserir_id_e_nome_medico,
    clicar_criar_tenant,
)


CAMINHO_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(CAMINHO_ENV)


def fluxo_criar_tenant():
    print("\n=== FLUXO: CRIAR TENANT ===")

    login_usuario = os.getenv("LOGIN_EMAIL")
    senha_usuario = os.getenv("LOGIN_SENHA")

    id_medico = "#199"
    nome_medico = "Mike Cardoso"

    if not login_usuario or not senha_usuario:
        raise ValueError("LOGIN_EMAIL ou LOGIN_SENHA não encontrados no arquivo .env")

    print("\n📌 Dados recebidos:")
    print(f"Login: {login_usuario}")

    driver = iniciar_chrome()

    try:
        print("\n🌐 Abrindo DoutorAgenda...")
        abrir_doutoriagenda(driver)

        print("🔐 Preenchendo login...")
        preencher_login(driver, login_usuario)

        print("🔑 Preenchendo senha...")
        preencher_senha(driver, senha_usuario)

        print("➡️ Clicando em entrar...")
        clicar_entrar(driver)

        print("⏳ Aguardando pós-login...")
        esperar_pos_login(driver)

        print("🖱️ Executando clique nas inicial...")
        clicar_elemento_iniciais(driver)

        print("🖱️ Clicando em trocar tenant...")
        clicar_trocar_tenant(driver)

        print("🖱️ Clicando no campo: Selecione o tenant para trocar")
        clicar_campo_Selecione_tenant_trocar(driver)

        print("🖱️ Inserindo o tenant para busca")
        inserir_id_medico(driver, id_medico)

        print("🔎 Extraindo os tenants da busca...")
        resultado = extrator_tenant_parecido(driver)

        print("🔎 Validando se o tenant é igual, parecido ou não existe...")
        existe_tenant, tenant_encontrado = analisar_tenant(resultado, id_medico)

        if existe_tenant:
            print(f"Tenant já existe: {tenant_encontrado}")
            return

        print("🔎 Fechando a caixa de busca...")
        fechar_modal_tenant(driver)

        print("🖱️ Executando clique nas inicial...")
        clicar_elemento_iniciais(driver)

        print("🖱️ Clicando em gerenciar tenant...")
        clicar_opcao_gerencia_tenant(driver)

        print("🖱️ Clicando criar novo tenant...")
        clicar_botao_tenant(driver)

        print("🖱️ Colando novo tenant...")
        inserir_id_e_nome_medico(driver, id_medico, nome_medico)

        print("🖱️ Simulando click...")
        clicar_criar_tenant()

        input("\nPressione ENTER para fechar...")

    except Exception as e:
        print(f"\n⚠️ Erro durante a execução do fluxo: {e}")
        input("Pressione ENTER para fechar...")

    finally:
        driver.quit()