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
from acoes.extrator_tenant_parecido import extrator_tenant_parecido
from acoes.analisador_tenant import analisar_tenant
from acoes.fechar_caixa_busca_tenant import fechar_modal_tenant
from backend.acoes.clicar_gerencia_tenant import clicar_opcao_gerencia_tenant
from backend.acoes.criar_novo_tenant import clicar_botao_tenant
from acoes.inserir_nome_novo_tenant import inserir_id_e_nome_medico,clicar_criar_tenant

def fluxo_criar_tenant():
    print("\n=== FLUXO: CRIAR TENANT ===")

    login_usuario = "(33) 99831-1030"
    senha_usuario = "254136Br."
    id_medico = "#199"
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

        print("🔎 Extraindo os tenants da busca...")
        resultado = extrator_tenant_parecido(driver)

        print("🔎 Validando se o tenant é igual, parecido ou não existe...")
        existe_tenant, tenant_encontrado = analisar_tenant(resultado, id_medico)

        if existe_tenant == True:
            exit()
        else:
            print("🔎 Fechando a caixa de busca...")
            fechar_modal_tenant(driver)

            print("🖱️ Executando clique nas inicial...")
            clicar_elemento_iniciais(driver)

            print("🖱️ Clicando em trocar tenant...")
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