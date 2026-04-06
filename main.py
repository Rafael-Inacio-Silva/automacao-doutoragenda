import os
from dotenv import load_dotenv
from fluxo_login_doutoriagenda import iniciar_safari, login_doutoriagenda


def main():
    load_dotenv()

    email = os.getenv("LOGIN_EMAIL")
    senha = os.getenv("LOGIN_SENHA")

    if not email or not senha:
        print("Erro: verifique se LOGIN_EMAIL, LOGIN_SENHA e LOGIN_SENHA_2 estão no .env")
        return

    driver = iniciar_safari()

    try:
        sucesso, mensagem = login_doutoriagenda(driver, email, senha)
        print(mensagem)

        if sucesso:
            input("Login realizado. Pressione ENTER para fechar o navegador...")
        else:
            input("Falha no login. Pressione ENTER para fechar o navegador...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()