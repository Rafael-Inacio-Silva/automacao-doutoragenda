📝 3. README PROFISSIONAL (PRONTO)
Copia e cola exatamente isso 👇
# 🤖 Automação de Login - DoutorAgenda

Projeto de automação web utilizando Python + Selenium para realizar login automatizado na plataforma DoutorAgenda, com tratamento de falhas e fallback de credenciais.

---

## 🚀 Objetivo

Este projeto tem como objetivo automatizar o processo de login na plataforma DoutorAgenda, simulando o comportamento humano e tratando cenários reais como:

- Tentativa de login com múltiplas credenciais
- Tratamento de erro de autenticação
- Reexecução de fluxo com fallback
- Preparação para automações futuras (extração de dados, interação com sistema, etc.)

---

## 🧠 Estratégia utilizada

A automação segue um fluxo estruturado:

1. Acessa a página de login
2. Preenche email
3. Tenta login com senha principal
4. Caso falhe:
   - Apaga a senha manualmente (evitando falha do `.clear()`)
   - Tenta segunda senha
5. Retorna status de sucesso ou erro

---

## 🛠️ Tecnologias utilizadas

- Python 3
- Selenium WebDriver
- Safari WebDriver
- python-dotenv

---

## 📁 Estrutura do projeto
automacao-doutoragenda/
│
├── main.py # Orquestrador principal
├── fluxo_login_doutoriagenda.py # Fluxo de login automatizado
├── .env # Credenciais (não versionado)
├── .gitignore
└── README.md

---

## 🔐 Configuração do ambiente

Crie um arquivo `.env` na raiz do projeto:
LOGIN_EMAIL=seu_email
LOGIN_SENHA_1=sua_senha_1
LOGIN_SENHA_2=sua_senha_2

---

## ▶️ Como executar

1. Instale as dependências:

```bash
pip install selenium python-dotenv
Execute o projeto:
python main.py
⚠️ Observações importantes
O projeto utiliza Safari WebDriver (Safari deve estar habilitado para automação)
O sistema pode apresentar verificações de segurança (captcha), que exigem interação manual
Os XPaths utilizados podem ser dinâmicos e podem exigir ajustes futuros
📌 Próximos passos
 Extração de dados após login
 Automação de navegação interna
 Download de prompts
 Salvamento estruturado (CSV/Excel)
 Tratamento de overlays e Shadow DOM
👨‍💻 Autor
Desenvolvido por Rafael Inácio Silva
Engenharia de Prompt | Automação | IA aplicada

---

# 💡 Dica estratégica (importante)

Isso aqui já tá com cara de projeto de:

👉 Automação real  
👉 Engenharia de Prompt + Ops  
👉 Produto  

Se quiser no próximo passo eu te ajudo a transformar isso em:

- projeto de portfólio forte  
- descrição pra LinkedIn  
- ou até argumento pra entrevista  

---

Se quiser agora, manda:

👉 “próximo: extrair HTML depois do login”  

que a gente já pluga direto no fluxo que você criou.
