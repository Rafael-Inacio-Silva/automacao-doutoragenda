import json
import os
import re
import unicodedata
from pathlib import Path


try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


# ============================================================
# UTILITÁRIOS GERAIS
# ============================================================

def _carregar_env():
    """
    Carrega o .env do projeto, caso ainda não tenha sido carregado pelo main.
    Caminho esperado:
    raiz_do_projeto/.env
    """

    if load_dotenv is None:
        return

    try:
        caminho_env = Path(__file__).resolve().parents[2] / ".env"
        load_dotenv(caminho_env)
        load_dotenv()
    except Exception:
        pass


def _normalizar_texto(texto):
    """
    Normaliza texto para comparação:
    - remove acentos
    - transforma em minúsculo
    - remove espaços extras
    """

    if texto is None:
        return ""

    texto = str(texto).strip()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip().lower()


def _resultado_para_texto(resultado):
    """
    Converte qualquer resultado em texto para facilitar validações.
    """

    if resultado is None:
        return ""

    if isinstance(resultado, (dict, list)):
        try:
            return json.dumps(resultado, ensure_ascii=False)
        except Exception:
            return str(resultado)

    return str(resultado)


def _extrair_linhas_resultado(resultado):
    """
    Extrai linhas úteis de um resultado que pode vir como:
    - string
    - lista
    - dicionário
    """

    if resultado is None:
        return []

    if isinstance(resultado, list):
        linhas = []

        for item in resultado:
            if isinstance(item, dict):
                linhas.append(_resultado_para_texto(item).strip())
            else:
                linhas.append(str(item).strip())

        return [linha for linha in linhas if linha]

    if isinstance(resultado, dict):
        for chave in [
            "tenants",
            "resultados",
            "resultado",
            "resultado_extracao",
            "linhas",
            "dados",
        ]:
            if chave in resultado:
                return _extrair_linhas_resultado(resultado.get(chave))

        texto = _resultado_para_texto(resultado)
        return [linha.strip() for linha in texto.splitlines() if linha.strip()]

    texto = str(resultado)
    return [linha.strip() for linha in texto.splitlines() if linha.strip()]


def _limitar_texto(texto, limite=800):
    """
    Limita texto grande para não poluir o relatório/log.
    """

    if texto is None:
        return ""

    texto = str(texto)

    if len(texto) <= limite:
        return texto

    return texto[:limite] + "... [texto cortado]"


# ============================================================
# REGRA 1 — TENANT 100% IGUAL AO ESPERADO
# ============================================================

def validar_tenant_igual_exato(resultado, tenant_esperado):
    """
    Regra 1:
    O tenant encontrado deve ser 100% igual ao tenant esperado.

    Exemplo esperado:
    #586 - Dr. Raphael Palomares Jacobs
    """

    titulo_regra = "Regra 1 — Tenant 100% igual ao esperado"

    tenant_esperado = str(tenant_esperado or "").strip()
    texto_resultado = _resultado_para_texto(resultado)
    linhas_resultado = _extrair_linhas_resultado(resultado)

    if resultado is None:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": tenant_esperado,
            "encontrado": None,
            "mensagem": "Nenhum resultado de tenant foi extraído.",
        }

    if "Nenhum tenant encontrado" in texto_resultado:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": tenant_esperado,
            "encontrado": "Nenhum tenant encontrado",
            "mensagem": "A busca retornou que nenhum tenant foi encontrado.",
        }

    tenant_encontrado_exato = None

    for linha in linhas_resultado:
        if linha == tenant_esperado:
            tenant_encontrado_exato = linha
            break

    if texto_resultado.strip() == tenant_esperado:
        tenant_encontrado_exato = texto_resultado.strip()

    if tenant_encontrado_exato:
        return {
            "regra": titulo_regra,
            "status": "aprovado",
            "esperado": tenant_esperado,
            "encontrado": tenant_encontrado_exato,
            "mensagem": "Tenant encontrado é 100% igual ao tenant esperado.",
        }

    return {
        "regra": titulo_regra,
        "status": "reprovado",
        "esperado": tenant_esperado,
        "encontrado": linhas_resultado if linhas_resultado else texto_resultado,
        "mensagem": "Nenhum tenant encontrado corresponde exatamente ao tenant esperado.",
    }


# ============================================================
# REGRA 2 — SUMARIZAÇÃO DE CONTEXTO DEVE ESTAR FALSE
# ============================================================

def validar_sumarizacao_contexto_false(valor_sumarizacao):
    """
    Regra 2:
    O campo Sumarização de Contexto deve estar com aria-checked="false".
    """

    titulo_regra = "Regra 2 — Sumarização de Contexto deve estar false"

    if valor_sumarizacao is None:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": "false",
            "encontrado": None,
            "mensagem": "Não foi possível extrair o valor de aria-checked da Sumarização de Contexto.",
        }

    valor_normalizado = str(valor_sumarizacao).strip().lower()

    if valor_normalizado == "false":
        return {
            "regra": titulo_regra,
            "status": "aprovado",
            "esperado": "false",
            "encontrado": valor_sumarizacao,
            "mensagem": "Sumarização de Contexto está corretamente desativada.",
        }

    return {
        "regra": titulo_regra,
        "status": "reprovado",
        "esperado": "false",
        "encontrado": valor_sumarizacao,
        "mensagem": "Sumarização de Contexto deveria estar false, mas foi encontrado outro valor.",
    }


# ============================================================
# REGRA 3 — ESTÁGIOS OBRIGATÓRIOS
# ============================================================

ESTAGIOS_OBRIGATORIOS = {
    "1": "Conexão",
    "2": "Qualificação",
    "3": "Agendamento",
    "4": "Confirmação",
}


def _buscar_estagio(dados_estagios, numero=None, nome=None):
    """
    Busca estágio por número ou nome.
    """

    if not isinstance(dados_estagios, dict):
        return None

    estagios = dados_estagios.get("estagios", [])

    if not isinstance(estagios, list):
        return None

    numero_procurado = str(numero).strip() if numero is not None else None
    nome_procurado = _normalizar_texto(nome) if nome is not None else None

    for estagio in estagios:
        numero_estagio = str(estagio.get("numero", "")).strip()
        nome_estagio = _normalizar_texto(estagio.get("nome", ""))

        if numero_procurado and numero_estagio == numero_procurado:
            return estagio

        if nome_procurado and nome_estagio == nome_procurado:
            return estagio

    return None


def validar_estagios_obrigatorios(dados_estagios):
    """
    Regra 3:
    Valida se os estágios obrigatórios estão corretos:

    Estágio 1 — Conexão
    Estágio 2 — Qualificação
    Estágio 3 — Agendamento
    Estágio 4 — Confirmação
    """

    titulo_regra = "Regra 3 — Estágios obrigatórios da conversa"

    if not isinstance(dados_estagios, dict):
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": ESTAGIOS_OBRIGATORIOS,
            "encontrado": None,
            "mensagem": "Dados dos estágios não foram recebidos em formato válido.",
        }

    estagios = dados_estagios.get("estagios", [])

    if not estagios:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": ESTAGIOS_OBRIGATORIOS,
            "encontrado": [],
            "mensagem": "Nenhum estágio foi encontrado para validação.",
        }

    problemas = []
    detalhes = []

    for numero_esperado, nome_esperado in ESTAGIOS_OBRIGATORIOS.items():
        estagio = _buscar_estagio(
            dados_estagios=dados_estagios,
            numero=numero_esperado,
        )

        if not estagio:
            problemas.append(
                f"Estágio {numero_esperado} não foi encontrado."
            )

            detalhes.append(
                {
                    "numero": numero_esperado,
                    "esperado": nome_esperado,
                    "encontrado": None,
                    "status": "reprovado",
                }
            )

            continue

        nome_encontrado = str(estagio.get("nome", "")).strip()

        nome_esperado_normalizado = _normalizar_texto(nome_esperado)
        nome_encontrado_normalizado = _normalizar_texto(nome_encontrado)

        if nome_encontrado_normalizado != nome_esperado_normalizado:
            problemas.append(
                f"Estágio {numero_esperado} deveria ser '{nome_esperado}', "
                f"mas foi encontrado '{nome_encontrado}'."
            )

            detalhes.append(
                {
                    "numero": numero_esperado,
                    "esperado": nome_esperado,
                    "encontrado": nome_encontrado,
                    "status": "reprovado",
                }
            )

            continue

        detalhes.append(
            {
                "numero": numero_esperado,
                "esperado": nome_esperado,
                "encontrado": nome_encontrado,
                "status": "aprovado",
            }
        )

    if not problemas:
        return {
            "regra": titulo_regra,
            "status": "aprovado",
            "esperado": ESTAGIOS_OBRIGATORIOS,
            "encontrado": detalhes,
            "mensagem": "Todos os estágios obrigatórios foram encontrados corretamente.",
            "detalhes": detalhes,
        }

    return {
        "regra": titulo_regra,
        "status": "reprovado",
        "esperado": ESTAGIOS_OBRIGATORIOS,
        "encontrado": detalhes,
        "mensagem": "Um ou mais estágios obrigatórios estão ausentes ou incorretos.",
        "problemas_encontrados": problemas,
        "detalhes": detalhes,
    }


# ============================================================
# REGRA 4 — VALIDAÇÃO LLM DO ESTÁGIO 3 AGENDAMENTO
# ============================================================

def _extrair_json_resposta_llm(texto):
    """
    Tenta transformar a resposta da LLM em JSON.
    Se vier texto antes ou depois, tenta extrair o primeiro bloco JSON.
    """

    if not texto:
        return None

    texto = str(texto).strip()

    try:
        return json.loads(texto)
    except Exception:
        pass

    encontrado = re.search(r"\{.*\}", texto, re.DOTALL)

    if not encontrado:
        return None

    try:
        return json.loads(encontrado.group(0))
    except Exception:
        return None


def _verificar_inicio_obrigatorio_agendamento(instrucao):
    """
    Validação objetiva do início obrigatório:

    INFORMAÇÕES SOBRE AGENDAMENTO:
    {{tipos_agendamento_context}}
    """

    if not instrucao:
        return False

    texto = str(instrucao)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n").strip()

    linhas = [
        linha.strip()
        for linha in texto.split("\n")
        if linha.strip()
    ]

    if len(linhas) < 2:
        return False

    primeira_linha = linhas[0]
    segunda_linha = linhas[1]

    return (
        primeira_linha == "INFORMAÇÕES SOBRE AGENDAMENTO:"
        and segunda_linha == "{{tipos_agendamento_context}}"
    )


def _chamar_openai_validacao_json(prompt_sistema, prompt_usuario):
    """
    Chama a OpenAI para validar a instrução do Estágio 3.

    A chave deve estar no .env:

    OPENAI_API_KEY=sua_chave
    OPENAI_MODEL=gpt-4o-mini

    Se OPENAI_MODEL não existir, usa gpt-4o-mini como padrão.
    """

    _carregar_env()

    chave_openai = os.getenv("OPENAI_API_KEY")

    if not chave_openai:
        raise RuntimeError("OPENAI_API_KEY não encontrada no .env.")

    modelo = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        from openai import OpenAI
    except Exception as erro_import:
        raise RuntimeError(
            "Biblioteca openai não instalada. Execute: pip install openai"
        ) from erro_import

    client = OpenAI(api_key=chave_openai)

    erro_responses = None

    try:
        resposta = client.responses.create(
            model=modelo,
            input=[
                {
                    "role": "system",
                    "content": prompt_sistema,
                },
                {
                    "role": "user",
                    "content": prompt_usuario,
                },
            ],
        )

        texto_resposta = getattr(resposta, "output_text", None)

        if not texto_resposta:
            texto_resposta = str(resposta)

        return {
            "modelo": modelo,
            "metodo": "responses",
            "texto": texto_resposta,
        }

    except Exception as erro:
        erro_responses = erro

    try:
        resposta = client.chat.completions.create(
            model=modelo,
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema,
                },
                {
                    "role": "user",
                    "content": prompt_usuario,
                },
            ],
        )

        texto_resposta = resposta.choices[0].message.content

        return {
            "modelo": modelo,
            "metodo": "chat.completions",
            "texto": texto_resposta,
        }

    except Exception as erro_chat:
        raise RuntimeError(
            f"Erro ao chamar OpenAI. "
            f"Erro responses: {erro_responses}. "
            f"Erro chat.completions: {erro_chat}"
        )


def validar_agendamento_estagio_3_llm(dados_estagios):
    """
    Regra 4:
    Valida por LLM se o Estágio 3 — Agendamento contém as regras obrigatórias:

    1. Proibir inventar, deduzir ou assumir horários disponíveis
    2. Obrigar executar buscar_proximos_horarios antes de oferecer horários
    3. Exigir parâmetros tipo_agendamento_id + quantidade_dias: 90
    4. Deixar claro que só pode oferecer horários após retorno da ferramenta
    5. Iniciar com:

       INFORMAÇÕES SOBRE AGENDAMENTO:
       {{tipos_agendamento_context}}
    """

    titulo_regra = "Regra 4 — Validação LLM do Estágio 3 Agendamento"

    if not isinstance(dados_estagios, dict):
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": "Dados extraídos da aba Conversa em formato válido.",
            "encontrado": None,
            "mensagem": "Dados dos estágios não foram recebidos em formato válido.",
        }

    estagio_3 = _buscar_estagio(
        dados_estagios=dados_estagios,
        numero="3",
    )

    if not estagio_3:
        estagio_3 = _buscar_estagio(
            dados_estagios=dados_estagios,
            nome="Agendamento",
        )

    if not estagio_3:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": "Encontrar o Estágio 3 ou um estágio com nome Agendamento.",
            "encontrado": None,
            "mensagem": "Não foi encontrado o Estágio 3/Agendamento para validação por LLM.",
        }

    instrucao = str(estagio_3.get("instrucao", "") or "").strip()

    if not instrucao:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": "Instrução preenchida no Estágio 3 — Agendamento.",
            "encontrado": {
                "numero": estagio_3.get("numero"),
                "nome": estagio_3.get("nome"),
                "id_instrucao": estagio_3.get("id_instrucao"),
                "instrucao": "",
            },
            "mensagem": "O Estágio 3 foi encontrado, mas a instrução está vazia.",
        }

    inicio_correto_codigo = _verificar_inicio_obrigatorio_agendamento(instrucao)

    prompt_sistema = """
Você é um validador de prompts do Estágio 3 (Agendamento) da plataforma Vekta.

Sua única função é verificar se o Estágio 3 recebido contém o elemento OBRIGATÓRIO:

ELEMENTO OBRIGATÓRIO DO ESTÁGIO 3:

Consultar agenda ANTES de oferecer horários usando buscar_proximos_horarios.

O prompt DEVE conter instruções EXPLÍCITAS que:

1. PROÍBAM inventar, deduzir ou assumir horários disponíveis
2. OBRIGUEM executar buscar_proximos_horarios ANTES de confirmar disponibilidade
3. ESPECIFIQUEM os parâmetros: tipo_agendamento_id + quantidade_dias: 90
4. DEIXEM CLARO que só pode oferecer horários APÓS receber retorno da ferramenta
5. INICIEM com exatamente:

INFORMAÇÕES SOBRE AGENDAMENTO:
{{tipos_agendamento_dinamico}}

CRITÉRIOS DE APROVAÇÃO:

APROVADO se contém:
- Regra explícita proibindo inventar/deduzir horários
- Instrução obrigatória para executar buscar_proximos_horarios antes de oferecer
- Menção aos parâmetros corretos da ferramenta
- Fluxo claro: consultar → aguardar retorno → oferecer
- Início correto com:
  INFORMAÇÕES SOBRE AGENDAMENTO:
  {{tipos_agendamento_dinamico}}

REPROVADO se:
- Não menciona a ferramenta buscar_proximos_horarios
- Permite assumir disponibilidade sem consultar
- Não deixa claro que consulta é obrigatória ANTES de qualquer oferta
- Faltam os parâmetros obrigatórios
- Não inicia com:
  INFORMAÇÕES SOBRE AGENDAMENTO:
  {{tipos_agendamento_dinamico}}

Responda SOMENTE em JSON válido, sem markdown, no formato:

{
  "status": "aprovado" ou "reprovado",
  "mensagem": "resumo objetivo da validação",
  "criterios": {
    "proibe_inventar_horarios": true ou false,
    "obriga_buscar_proximos_horarios_antes": true ou false,
    "menciona_tipo_agendamento_id": true ou false,
    "menciona_quantidade_dias_90": true ou false,
    "so_oferece_apos_retorno": true ou false,
    "inicio_correto": true ou false
  },
  "problemas_encontrados": [
    "lista objetiva dos problemas encontrados"
  ]
}
"""

    prompt_usuario = f"""
Valide o prompt abaixo do Estágio 3 — Agendamento.

DADOS DO ESTÁGIO:
Número: {estagio_3.get("numero")}
Nome: {estagio_3.get("nome")}
ID da instrução: {estagio_3.get("id_instrucao")}

INSTRUÇÃO DO ESTÁGIO:
{instrucao}
"""

    try:
        resposta_openai = _chamar_openai_validacao_json(
            prompt_sistema=prompt_sistema,
            prompt_usuario=prompt_usuario,
        )

        texto_resposta = resposta_openai.get("texto", "")
        avaliacao_llm = _extrair_json_resposta_llm(texto_resposta)

        if not avaliacao_llm:
            return {
                "regra": titulo_regra,
                "status": "reprovado",
                "esperado": "Resposta JSON válida da LLM.",
                "encontrado": _limitar_texto(texto_resposta, limite=1000),
                "mensagem": "A LLM respondeu, mas a resposta não veio em JSON válido.",
                "dados_estagio_validado": {
                    "numero": estagio_3.get("numero"),
                    "nome": estagio_3.get("nome"),
                    "id_instrucao": estagio_3.get("id_instrucao"),
                    "inicio_correto_codigo": inicio_correto_codigo,
                },
                "modelo_llm": resposta_openai.get("modelo"),
                "metodo_llm": resposta_openai.get("metodo"),
            }

        status_llm = str(avaliacao_llm.get("status", "")).strip().lower()

        if status_llm not in ["aprovado", "reprovado"]:
            status_llm = "reprovado"

        criterios = avaliacao_llm.get("criterios", {})

        if not isinstance(criterios, dict):
            criterios = {}

        criterios["inicio_correto"] = inicio_correto_codigo

        problemas_encontrados = avaliacao_llm.get("problemas_encontrados", [])

        if not isinstance(problemas_encontrados, list):
            problemas_encontrados = [str(problemas_encontrados)]

        if not inicio_correto_codigo:
            problema_inicio = (
                "A instrução não inicia exatamente com: "
                "INFORMAÇÕES SOBRE AGENDAMENTO: "
                "{{tipos_agendamento_context}}"
            )

            if problema_inicio not in problemas_encontrados:
                problemas_encontrados.append(problema_inicio)

        status_final = "aprovado"

        if status_llm != "aprovado":
            status_final = "reprovado"

        if not inicio_correto_codigo:
            status_final = "reprovado"

        mensagem_llm = avaliacao_llm.get(
            "mensagem",
            "Validação LLM executada.",
        )

        if status_final == "aprovado":
            mensagem_final = (
                "Estágio 3 — Agendamento aprovado na validação LLM."
            )
        else:
            mensagem_final = mensagem_llm

        return {
            "regra": titulo_regra,
            "status": status_final,
            "esperado": {
                "ferramenta": "buscar_proximos_horarios",
                "parametros_obrigatorios": [
                    "tipo_agendamento_id",
                    "quantidade_dias: 90",
                ],
                "fluxo_obrigatorio": "consultar agenda → aguardar retorno → oferecer horários",
                "inicio_obrigatorio": [
                    "INFORMAÇÕES SOBRE AGENDAMENTO:",
                    "{{tipos_agendamento_context}}",
                ],
            },
            "encontrado": {
                "numero": estagio_3.get("numero"),
                "nome": estagio_3.get("nome"),
                "id_instrucao": estagio_3.get("id_instrucao"),
                "inicio_correto_codigo": inicio_correto_codigo,
                "instrucao_preview": _limitar_texto(instrucao, limite=500),
            },
            "mensagem": mensagem_final,
            "criterios": criterios,
            "problemas_encontrados": problemas_encontrados,
            "resposta_llm": avaliacao_llm,
            "modelo_llm": resposta_openai.get("modelo"),
            "metodo_llm": resposta_openai.get("metodo"),
        }

    except Exception as erro:
        return {
            "regra": titulo_regra,
            "status": "reprovado",
            "esperado": "Executar validação LLM com sucesso.",
            "encontrado": "Erro durante chamada da OpenAI.",
            "mensagem": f"Erro na validação LLM: {erro}",
            "dados_estagio_validado": {
                "numero": estagio_3.get("numero"),
                "nome": estagio_3.get("nome"),
                "id_instrucao": estagio_3.get("id_instrucao"),
                "inicio_correto_codigo": inicio_correto_codigo,
                "instrucao_preview": _limitar_texto(instrucao, limite=500),
            },
        }