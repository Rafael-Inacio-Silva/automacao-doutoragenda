from acoes.iniciar_safari import iniciar_chrome
from acoes.abrir_doutoriagenda import abrir_doutoriagenda
from acoes.login import (
    preencher_login,
    preencher_senha,
    clicar_entrar,
    esperar_pos_login
)
from acoes.clicar_iniciais import clicar_elemento_iniciais
from acoes.clicar_trocar_tenant import clicar_trocar_tenant
from acoes.clicar_campo_Selecione_tenant_trocar import clicar_campo_Selecione_tenant_trocar
from acoes.inserir_id_medico import inserir_id_medico
from acoes.extrator_tenant_parecido import extrator_tenant_parecido


def fluxo_criar_tenant():
    print("\n=== FLUXO: CRIAR TENANT ===")

    # login_usuario = input("Digite o login: ").strip()
    # senha_usuario = input("Digite a senha: ").strip()
    login_usuario = "(33) 99831-1030"
    senha_usuario = "254136Br."
    #id_medico = input("Digite o ID do médico: ").strip()
    #nome_medico = input("Digite o nome do médico: ").strip()

    print("\n📌 Dados recebidos:")
    print(f"Login: {login_usuario}")
    #print(f"ID do médico: {id_medico}")
    #print(f"Nome do médico: {nome_medico}")

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
        inserir_id_medico(driver)

        print("🔎 Validando se o tenant é igual, parecido ou não existe...")
        resultado = extrator_tenant_parecido(driver)
        print(resultado)

        input("\nPressione ENTER para fechar...")

    except Exception as e:
        print(f"\n⚠️ Erro durante a execução do fluxo: {e}")
        input("Pressione ENTER para fechar...")

    finally:
        driver.quit()