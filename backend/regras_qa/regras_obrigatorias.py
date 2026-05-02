def validar_tenant_igual_exato(resultado, tenant_esperado):
   """
   Regra obrigatória:
   O tenant encontrado deve ser 100% igual ao tenant esperado.

   Retorna um dicionário padronizado para relatório.
   """

   if "Nenhum tenant encontrado" in resultado:
    return {
     "regra": "Tenant 100% igual ao esperado",
     "status": "reprovado",
     "esperado": tenant_esperado,
     "encontrado": None,
     "mensagem": "Nenhum tenant encontrado."
    }

   tenant_esperado_limpo = tenant_esperado.strip()

   for item in resultado:
    item_limpo = item.strip()

    if item_limpo == tenant_esperado_limpo:
     return {
      "regra": "Tenant 100% igual ao esperado",
      "status": "aprovado",
      "esperado": tenant_esperado_limpo,
      "encontrado": item_limpo,
      "mensagem": "Tenant encontrado 100% igual ao esperado."
     }

   return {
    "regra": "Tenant 100% igual ao esperado",
    "status": "reprovado",
    "esperado": tenant_esperado_limpo,
    "encontrado": resultado,
    "mensagem": "Nenhum tenant 100% igual foi encontrado."
   }