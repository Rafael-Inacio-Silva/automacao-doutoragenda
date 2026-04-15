def analisar_tenant(resultado, id_medico):
    """
    Retorna:
        True, tenant_encontrado -> se existe ID exato
        False, None -> se não existe ID exato
    """

    if "Nenhum tenant encontrado" in resultado:
        print("✅ Tenant não existe.")
        print("Criar")
        return False, None

    encontrou_id_exato = None

    for item in resultado:
        item_limpo = item.strip()

        # pega tudo antes do primeiro espaço
        id_extraido = item_limpo.split(" ")[0]

        if id_extraido == id_medico:
            encontrou_id_exato = item_limpo
            break

    if encontrou_id_exato:
        print("⛔ Já existe tenant com esse ID.")
        print(f"✅ Item encontrado: {encontrou_id_exato}")
        print("não criar")
        return True, encontrou_id_exato

    else:
        print(f"⚠️ Existem tenants parecidos, mas não com esse ID exato: {resultado}")
        print("Criar")
        return False, None