from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extrair_valor_sumarizacao_contexto(driver):
 """
 Extrai o valor do atributo aria-checked do botão relacionado ao label:
 Sumarização de Contexto.

 A busca principal usa o texto do label, porque o id radix pode mudar.
 """

 wait = WebDriverWait(driver, 10)

 try:
  xpath_botao_pelo_label = (
   "//label[normalize-space()='Sumarização de Contexto']"
   "/ancestor::div[.//button[@aria-checked]][1]"
   "//button[@aria-checked]"
  )

  botao_sumarizacao = wait.until(
   EC.presence_of_element_located(
    (By.XPATH, xpath_botao_pelo_label)
   )
  )

  valor_aria_checked = botao_sumarizacao.get_attribute("aria-checked")

  return {
   "status_extracao": "encontrado",
   "campo": "Sumarização de Contexto",
   "atributo": "aria-checked",
   "valor": valor_aria_checked,
   "metodo_busca": "label_texto"
  }

 except Exception as erro_label:
  try:
   xpath_botao_absoluto = (
    '//*[@id="radix-_r_bn_-content-basic"]/div/div[1]/div[2]/div[6]/button'
   )

   botao_sumarizacao = wait.until(
    EC.presence_of_element_located(
     (By.XPATH, xpath_botao_absoluto)
    )
   )

   valor_aria_checked = botao_sumarizacao.get_attribute("aria-checked")

   return {
    "status_extracao": "encontrado",
    "campo": "Sumarização de Contexto",
    "atributo": "aria-checked",
    "valor": valor_aria_checked,
    "metodo_busca": "xpath_absoluto",
    "observacao": "Busca pelo label falhou, mas o XPath absoluto funcionou."
   }

  except Exception as erro_xpath_absoluto:
   return {
    "status_extracao": "nao_encontrado",
    "campo": "Sumarização de Contexto",
    "atributo": "aria-checked",
    "valor": None,
    "metodo_busca": "label_texto_e_xpath_absoluto",
    "erro_label": str(erro_label),
    "erro_xpath_absoluto": str(erro_xpath_absoluto),
   }