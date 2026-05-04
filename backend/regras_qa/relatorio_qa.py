import json
from pathlib import Path
from datetime import datetime


PASTA_REGRAS_QA = Path(__file__).resolve().parent

CAMINHO_RELATORIO_TXT = PASTA_REGRAS_QA / "relatorio_qa.txt"
CAMINHO_LOG_JSON = PASTA_REGRAS_QA / "log_qa.json"


def preparar_arquivos_resultado():
    """
    Apaga os arquivos da execução anterior e prepara novos arquivos.
    """

    if CAMINHO_RELATORIO_TXT.exists():
        CAMINHO_RELATORIO_TXT.unlink()

    if CAMINHO_LOG_JSON.exists():
        CAMINHO_LOG_JSON.unlink()


def salvar_log_json(eventos):
    """
    Salva o log estruturado da execução em JSON.
    """

    with open(CAMINHO_LOG_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(eventos, arquivo, ensure_ascii=False, indent=4)


def adicionar_evento_log(eventos, etapa, status, mensagem, dados=None):
    """
    Adiciona um evento ao log JSON.
    """

    eventos.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "fluxo": "testar_agente_qa",
            "etapa": etapa,
            "status": status,
            "mensagem": mensagem,
            "dados": dados or {},
        }
    )

    salvar_log_json(eventos)


def formatar_resultado_regra(numero_regra, resultado_regra):
    """
    Formata uma regra QA para o relatório TXT.
    """

    regra = resultado_regra.get("regra", f"Regra {numero_regra}")
    status = resultado_regra.get("status", "não informado")
    mensagem = resultado_regra.get("mensagem", "Sem mensagem.")
    esperado = resultado_regra.get("esperado", "Não informado")
    encontrado = resultado_regra.get("encontrado", "Não informado")

    return f"""
------------------------------------------------------------
REGRA {numero_regra}
------------------------------------------------------------
Nome da regra: {regra}
Status: {status}

Mensagem:
{mensagem}

Esperado:
{esperado}

Encontrado:
{encontrado}
"""


def contar_regras_aprovadas(resultados_regras):
    """
    Conta regras aprovadas conforme os status usados nas validações.
    """

    status_aprovados = ["aprovado", "sucesso", "ok", "passou", "conforme"]

    return sum(
        1
        for regra in resultados_regras
        if str(regra.get("status", "")).lower() in status_aprovados
    )


def gerar_relatorio_txt(status_geral, id_medico_teste, resultados_regras):
    """
    Gera o relatório TXT final para exibição no frontend.
    """

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    total_regras = len(resultados_regras)
    total_aprovadas = contar_regras_aprovadas(resultados_regras)
    total_reprovadas = total_regras - total_aprovadas

    conteudo = f"""
============================================================
              RELATÓRIO DE TESTE QA DO AGENTE
============================================================

Data da execução: {agora}
Status geral: {status_geral}
Tenant testado: {id_medico_teste}

Resumo:
- Total de regras testadas: {total_regras}
- Regras aprovadas: {total_aprovadas}
- Regras com alerta/reprovação: {total_reprovadas}

============================================================
                   RESULTADO DAS REGRAS
============================================================
"""

    for indice, resultado_regra in enumerate(resultados_regras, start=1):
        conteudo += formatar_resultado_regra(indice, resultado_regra)

    conteudo += """
============================================================
                     FIM DO RELATÓRIO
============================================================
"""

    with open(CAMINHO_RELATORIO_TXT, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo.strip())

    return str(CAMINHO_RELATORIO_TXT)


def gerar_relatorio_erro_txt(mensagem_erro, id_medico_teste):
    """
    Gera relatório TXT quando o fluxo falha antes de executar as regras.
    """

    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    conteudo = f"""
============================================================
RELATÓRIO DE TESTE QA DO AGENTE
============================================================

Data da execução: {agora}
Status geral: erro
Tenant testado: {id_medico_teste}

============================================================
ERRO NA EXECUÇÃO
============================================================

{mensagem_erro}

============================================================
FIM DO RELATÓRIO
============================================================
"""

    with open(CAMINHO_RELATORIO_TXT, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo.strip())

    return str(CAMINHO_RELATORIO_TXT)


def obter_caminho_log_json():
    """
    Retorna o caminho do log JSON.
    """

    return str(CAMINHO_LOG_JSON)


def obter_caminho_relatorio_txt():
    """
    Retorna o caminho do relatório TXT.
    """

    return str(CAMINHO_RELATORIO_TXT)