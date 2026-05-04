import json
from pathlib import Path
from queue import Queue
from threading import Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from backend.fluxo.criar_tenant import (
    fluxo_criar_tenant,
    limpar_arquivo_resultado_tenant,
    limpar_arquivo_log_tenant,
    CAMINHO_RESULTADO_TENANT,
    CAMINHO_LOG_TENANT,
)

from backend.fluxo.extrair_zarpon import (
    fluxo_extrair_prompts,
    limpar_arquivo_resultado_prompts,
    limpar_arquivo_log_prompts,
    CAMINHO_RESULTADO_PROMPTS,
    CAMINHO_LOG_PROMPTS,
)

from backend.fluxo.testar_agente import (
    fluxo_testar_agentes,
)

from backend.regras_qa.relatorio_qa import (
    preparar_arquivos_resultado,
    obter_caminho_log_json,
)


app = FastAPI(title="Automacao DrIA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CAMINHO_RAIZ = Path(__file__).resolve().parents[1]

# =====================================================
# CAMINHOS — QA
# =====================================================

CAMINHO_RESULTADO_QA = CAMINHO_RAIZ / "resultado_qa_lote.txt"
CAMINHO_LOG_QA = Path(obter_caminho_log_json())


def formatar_evento(evento):
    dados = json.dumps(evento, ensure_ascii=False)
    return f"data: {dados}\n\n"


@app.get("/")
def home():
    return {
        "mensagem": "Backend da Automação DrIA está rodando.",
        "arquivo_prompts": str(CAMINHO_RESULTADO_PROMPTS),
        "arquivo_log_prompts": str(CAMINHO_LOG_PROMPTS),
        "arquivo_tenant": str(CAMINHO_RESULTADO_TENANT),
        "arquivo_log_tenant": str(CAMINHO_LOG_TENANT),
        "arquivo_qa": str(CAMINHO_RESULTADO_QA),
        "arquivo_log_qa": str(CAMINHO_LOG_QA),
    }


# =====================================================
# DOWNLOADS — PROMPTS
# =====================================================

@app.get("/download/prompts")
def download_prompts():
    """
    Baixa o CSV da execução de prompts.
    Se o arquivo não existir, cria vazio com cabeçalho.
    """

    if not CAMINHO_RESULTADO_PROMPTS.exists():
        limpar_arquivo_resultado_prompts()

    return FileResponse(
        path=CAMINHO_RESULTADO_PROMPTS,
        filename="resultado_prompts.csv",
        media_type="text/csv",
    )


@app.get("/download/log-prompts")
def download_log_prompts():
    """
    Baixa o JSON de log da extração de prompts.
    Se o arquivo não existir, cria vazio.
    """

    if not CAMINHO_LOG_PROMPTS.exists():
        limpar_arquivo_log_prompts()

    return FileResponse(
        path=CAMINHO_LOG_PROMPTS,
        filename="log_extracao_prompts.json",
        media_type="application/json",
    )


# =====================================================
# DOWNLOADS — TENANT
# =====================================================

@app.get("/download/tenant")
def download_tenant():
    """
    Baixa o CSV do resultado da criação de tenant.
    Se o arquivo não existir, cria vazio com cabeçalho.
    """

    if not CAMINHO_RESULTADO_TENANT.exists():
        limpar_arquivo_resultado_tenant()

    return FileResponse(
        path=CAMINHO_RESULTADO_TENANT,
        filename="resultado_tenant.csv",
        media_type="text/csv",
    )


@app.get("/download/log-tenant")
def download_log_tenant():
    """
    Baixa o JSON de log da criação de tenant.
    Se o arquivo não existir, cria vazio.
    """

    if not CAMINHO_LOG_TENANT.exists():
        limpar_arquivo_log_tenant()

    return FileResponse(
        path=CAMINHO_LOG_TENANT,
        filename="log_tenant.json",
        media_type="application/json",
    )


# =====================================================
# DOWNLOADS — QA
# =====================================================

@app.get("/download/qa")
def download_qa():
    """
    Baixa o TXT consolidado do teste QA.
    Se o arquivo não existir, cria um TXT informativo.
    """

    if not CAMINHO_RESULTADO_QA.exists():
        with open(CAMINHO_RESULTADO_QA, "w", encoding="utf-8") as arquivo:
            arquivo.write("Nenhum relatório QA foi gerado ainda.")

    return FileResponse(
        path=CAMINHO_RESULTADO_QA,
        filename="resultado_qa_lote.txt",
        media_type="text/plain",
    )


@app.get("/download/qa-relatorio")
def download_qa_relatorio():
    """
    Alias para baixar o relatório QA.
    """

    return download_qa()


@app.get("/download/log-qa")
def download_log_qa():
    """
    Baixa o JSON de log do teste QA.
    Se o arquivo não existir, cria vazio.
    """

    if not CAMINHO_LOG_QA.exists():
        with open(CAMINHO_LOG_QA, "w", encoding="utf-8") as arquivo:
            json.dump([], arquivo, ensure_ascii=False, indent=2)

    return FileResponse(
        path=CAMINHO_LOG_QA,
        filename="log_qa.json",
        media_type="application/json",
    )


# =====================================================
# STREAM — CRIAR TENANT
# =====================================================

@app.get("/executar/criar-tenant-stream")
def executar_criar_tenant_stream(id_medico: str, nome_medico: str):
    fila = Queue()

    def enviar_log(evento):
        fila.put(evento)

    def executar_fluxo():
        try:
            # Limpa os arquivos do tenant no início de cada nova execução
            limpar_arquivo_resultado_tenant()
            limpar_arquivo_log_tenant()

            fila.put(
                {
                    "etapa": "arquivo",
                    "status": "concluido",
                    "mensagem": "Arquivos anteriores de tenant e log foram limpos para uma nova execução.",
                    "dados": {
                        "arquivo": str(CAMINHO_RESULTADO_TENANT),
                        "log": str(CAMINHO_LOG_TENANT),
                    },
                }
            )

            resultado = fluxo_criar_tenant(
                id_medico=id_medico,
                nome_medico=nome_medico,
                log=enviar_log,
            )

            if isinstance(resultado, dict):
                fila.put(
                    {
                        "etapa": "finalizacao",
                        "status": "concluido" if resultado.get("sucesso") else "erro",
                        "mensagem": resultado.get("mensagem", "Fluxo finalizado."),
                        "dados": {
                            "id_medico": id_medico,
                            "nome_medico": nome_medico,
                            "tenant": resultado.get("tenant", ""),
                            "status": resultado.get("status"),
                            "arquivo": str(CAMINHO_RESULTADO_TENANT),
                            "log": str(CAMINHO_LOG_TENANT),
                        },
                    }
                )

            else:
                fila.put(
                    {
                        "etapa": "finalizacao",
                        "status": "concluido",
                        "mensagem": "Fluxo Criar Tenant finalizado.",
                        "dados": {
                            "arquivo": str(CAMINHO_RESULTADO_TENANT),
                            "log": str(CAMINHO_LOG_TENANT),
                        },
                    }
                )

        except Exception as erro:
            fila.put(
                {
                    "etapa": "finalizacao",
                    "status": "erro",
                    "mensagem": f"Erro ao executar Criar Tenant: {erro}",
                    "dados": {
                        "arquivo": str(CAMINHO_RESULTADO_TENANT),
                        "log": str(CAMINHO_LOG_TENANT),
                    },
                }
            )

        finally:
            fila.put("__FIM__")

    def gerar_eventos():
        thread = Thread(target=executar_fluxo, daemon=True)
        thread.start()

        while True:
            evento = fila.get()

            if evento == "__FIM__":
                yield "event: finalizado\ndata: {}\n\n"
                break

            yield formatar_evento(evento)

    return StreamingResponse(
        gerar_eventos(),
        media_type="text/event-stream",
    )


# =====================================================
# STREAM — EXTRAIR PROMPTS
# =====================================================

@app.get("/executar/extrair-prompts-stream")
def executar_extrair_prompts_stream(email_medico: str, limpar_arquivo: bool = False):
    fila = Queue()

    def enviar_log(evento):
        fila.put(evento)

    def executar_fluxo():
        try:
            # =====================================================
            # LIMPA OS ARQUIVOS SOMENTE QUANDO O FRONT MANDAR
            # limpar_arquivo=true
            # =====================================================

            if limpar_arquivo:
                limpar_arquivo_resultado_prompts()
                limpar_arquivo_log_prompts()

                fila.put(
                    {
                        "etapa": "arquivo",
                        "status": "concluido",
                        "mensagem": "Arquivos anteriores de prompts e log foram limpos para uma nova execução.",
                        "dados": {
                            "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
                            "log": str(CAMINHO_LOG_PROMPTS),
                        },
                    }
                )

            # =====================================================
            # EXECUTA O FLUXO DE EXTRAÇÃO DO E-MAIL ATUAL
            # =====================================================

            resultado = fluxo_extrair_prompts(
                email_medico=email_medico,
                log=enviar_log,
            )

            if isinstance(resultado, dict):
                fila.put(
                    {
                        "etapa": "finalizacao",
                        "status": "concluido" if resultado.get("sucesso") else "erro",
                        "mensagem": resultado.get("mensagem", "Fluxo finalizado."),
                        "dados": {
                            "email_medico": resultado.get("email_medico"),
                            "quantidade_prompts": resultado.get("quantidade_prompts", 0),
                            "arquivo": resultado.get("arquivo", str(CAMINHO_RESULTADO_PROMPTS)),
                            "log": resultado.get("log", str(CAMINHO_LOG_PROMPTS)),
                            "status": resultado.get("status"),
                        },
                    }
                )

            else:
                fila.put(
                    {
                        "etapa": "finalizacao",
                        "status": "concluido",
                        "mensagem": "Fluxo Extrair Prompts finalizado.",
                        "dados": {
                            "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
                            "log": str(CAMINHO_LOG_PROMPTS),
                        },
                    }
                )

        except Exception as erro:
            fila.put(
                {
                    "etapa": "finalizacao",
                    "status": "erro",
                    "mensagem": f"Erro ao executar Extrair Prompts: {erro}",
                    "dados": {
                        "arquivo": str(CAMINHO_RESULTADO_PROMPTS),
                        "log": str(CAMINHO_LOG_PROMPTS),
                    },
                }
            )

        finally:
            fila.put("__FIM__")

    def gerar_eventos():
        thread = Thread(target=executar_fluxo, daemon=True)
        thread.start()

        while True:
            evento = fila.get()

            if evento == "__FIM__":
                yield "event: finalizado\ndata: {}\n\n"
                break

            yield formatar_evento(evento)

    return StreamingResponse(
        gerar_eventos(),
        media_type="text/event-stream",
    )


# =====================================================
# STREAM — TESTAR AGENTES QA
# =====================================================

@app.get("/executar/testar-agentes-qa-stream")
def executar_testar_agentes_qa_stream(tenants: str, limpar_arquivo: bool = True):
    """
    Executa o teste QA de agentes.

    O frontend pode enviar:

    tenants=#586 - Dr. Raphael Palomares Jacobs

    ou vários, separados por quebra de linha:

    tenants=#586 - Dr. Raphael Palomares Jacobs
    #267 - Dra. Maria Teste
    #199 - Dr. Mike Cardoso
    """

    fila = Queue()

    def enviar_log(evento):
        fila.put(evento)

    def executar_fluxo():
        try:
            # =====================================================
            # LIMPA OS ARQUIVOS NO INÍCIO DA EXECUÇÃO QA
            # =====================================================

            if limpar_arquivo:
                preparar_arquivos_resultado()

                fila.put(
                    {
                        "etapa": "arquivo",
                        "status": "concluido",
                        "mensagem": "Arquivos anteriores de QA e log foram limpos para uma nova execução.",
                        "dados": {
                            "arquivo": str(CAMINHO_RESULTADO_QA),
                            "log": str(CAMINHO_LOG_QA),
                        },
                    }
                )

            # =====================================================
            # EXECUTA O FLUXO QA
            # Pode receber 1 ou vários tenants no mesmo parâmetro
            # =====================================================

            resultado = fluxo_testar_agentes(
                tenants_texto=tenants,
                log=enviar_log,
            )

            if isinstance(resultado, dict):
                status_finalizacao = "concluido"

                if resultado.get("status") == "erro":
                    status_finalizacao = "erro"

                fila.put(
                    {
                        "etapa": "finalizacao",
                        "status": status_finalizacao,
                        "mensagem": resultado.get("mensagem", "Fluxo QA finalizado."),
                        "dados": {
                            "teste": resultado.get("teste"),
                            "quantidade": resultado.get("quantidade", 0),
                            "aprovados": resultado.get("aprovados", 0),
                            "reprovados": resultado.get("reprovados", 0),
                            "erros": resultado.get("erros", 0),
                            "arquivo": resultado.get("relatorio_txt", str(CAMINHO_RESULTADO_QA)),
                            "log": resultado.get("log_json", str(CAMINHO_LOG_QA)),
                            "status": resultado.get("status"),
                        },
                    }
                )

            else:
                fila.put(
                    {
                        "etapa": "finalizacao",
                        "status": "concluido",
                        "mensagem": "Fluxo Testar Agentes QA finalizado.",
                        "dados": {
                            "arquivo": str(CAMINHO_RESULTADO_QA),
                            "log": str(CAMINHO_LOG_QA),
                        },
                    }
                )

        except Exception as erro:
            fila.put(
                {
                    "etapa": "finalizacao",
                    "status": "erro",
                    "mensagem": f"Erro ao executar Testar Agentes QA: {erro}",
                    "dados": {
                        "arquivo": str(CAMINHO_RESULTADO_QA),
                        "log": str(CAMINHO_LOG_QA),
                    },
                }
            )

        finally:
            fila.put("__FIM__")

    def gerar_eventos():
        thread = Thread(target=executar_fluxo, daemon=True)
        thread.start()

        while True:
            evento = fila.get()

            if evento == "__FIM__":
                yield "event: finalizado\ndata: {}\n\n"
                break

            yield formatar_evento(evento)

    return StreamingResponse(
        gerar_eventos(),
        media_type="text/event-stream",
    )