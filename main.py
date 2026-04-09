from fluxo.criar_tenant import fluxo_criar_tenant


def exibir_menu():
    print("\n==============================")
    print("      MENU DE AUTOMAÇÃO")
    print("==============================")
    print("1 - Criar tenant")
    print("0 - Sair")
    print("==============================")


def main():
    while True:
        exibir_menu()
        #opcao = input("Escolha uma opção: ").strip()
        opcao = "1"

        if opcao == "1":
            fluxo_criar_tenant()

        elif opcao == "0":
            print("Encerrando o programa...")
            break

        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()