from backend.acoes.iniciar_navegador import iniciar_chrome
from backend.acoes.abrir_doutoriagenda import abrir_doutoriagenda
from backend.acoes.login import (
    preencher_login,
    preencher_senha,
    clicar_entrar,
    esperar_pos_login
)
from acoes.clicar_iniciais import clicar_elemento_iniciais
from backend.acoes.clicar_trocar_tenant import clicar_trocar_tenant
from backend.acoes.clicar_campo_Selecione_tenant_trocar import clicar_campo_Selecione_tenant_trocar
from backend.acoes.inserir_id_medico import inserir_id_medico
from acoes.clicar_primeiro_tenant import clicar_primeiro_tenant
from acoes.extrator_tenant_parecido import extrator_tenant_parecido
from acoes.analisador_tenant import analisar_tenant
from acoes.fechar_caixa_busca_tenant import fechar_modal_tenant
from acoes.inserir_nome_novo_tenant import inserir_id_e_nome_medico,clicar_criar_tenant

def fluxo_criar_agente():
    print("\n=== FLUXO: CRIAR TENANT ===")

    login_usuario = "(33) 99831-1030"
    senha_usuario = "254136Br."
    id_medico = "Conta teste"
    nome_medico = "Mike Cardoso"
    #id_medico = input("Digite o ID do médico: ").strip()
    #nome_medico = input("Digite o nome do médico: ").strip()

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

        print("🖱️ Clicar primeiro Tenant da busca")
        clicar_primeiro_tenant(driver)

        input("\nPressione ENTER para fechar...")

    except Exception as e:
        print(f"\n⚠️ Erro durante a execução do fluxo: {e}")
        input("Pressione ENTER para fechar...")

    finally:
        driver.quit()