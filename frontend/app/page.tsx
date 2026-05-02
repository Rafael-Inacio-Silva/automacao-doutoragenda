"use client";

import { useState } from "react";
import Sidebar from "../components/Sidebar";
import StatusPanel from "../components/StatusPanel";

type Status = "pendente" | "executando" | "concluido" | "erro" | "alerta";

type ChecklistItem = {
  etapa: string;
  titulo: string;
  status: Status;
};

type ResultadoPrompt = {
  email: string;
  status: "pendente" | "executando" | "executado";
  quantidadePrompts: number;
  mensagem: string;
};

const statusTenantInicial: ChecklistItem[] = [
  { etapa: "navegador", titulo: "Abrir navegador", status: "pendente" },
  { etapa: "acesso", titulo: "Acessar DoutorAgenda", status: "pendente" },
  { etapa: "login", titulo: "Realizar login", status: "pendente" },
  { etapa: "busca_tenant", titulo: "Verificar se o tenant já existe", status: "pendente" },
  { etapa: "criacao_tenant", titulo: "Criar novo tenant", status: "pendente" },
  { etapa: "finalizacao", titulo: "Finalizar automação", status: "pendente" },
];

const statusPromptsInicial: ChecklistItem[] = [
  { etapa: "navegador", titulo: "Abrir navegador", status: "pendente" },
  { etapa: "login", titulo: "Realizar login", status: "pendente" },
  { etapa: "extracao", titulo: "Extrair prompts", status: "pendente" },
  { etapa: "finalizacao", titulo: "Finalizar extração", status: "pendente" },
];

export default function Page() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const [carregando, setCarregando] = useState("");
  const [fluxoSelecionado, setFluxoSelecionado] = useState<"tenant" | "prompts" | null>(null);

  const [statusTenant, setStatusTenant] = useState<ChecklistItem[]>(statusTenantInicial);
  const [statusPrompts, setStatusPrompts] = useState<ChecklistItem[]>(statusPromptsInicial);

  const [idMedico, setIdMedico] = useState("");
  const [nomeMedico, setNomeMedico] = useState("");

  const [emailsTexto, setEmailsTexto] = useState("");
  const [resultadosPrompts, setResultadosPrompts] = useState<ResultadoPrompt[]>([]);

  function atualizarStatusTenant(etapa: string, status: Status) {
    setStatusTenant((itensAtuais) =>
      itensAtuais.map((item) =>
        item.etapa === etapa ? { ...item, status } : item
      )
    );
  }

  function atualizarStatusPrompts(etapa: string, status: Status) {
    setStatusPrompts((itensAtuais) =>
      itensAtuais.map((item) =>
        item.etapa === etapa ? { ...item, status } : item
      )
    );
  }

  function abrirFormCriarTenant() {
    setFluxoSelecionado("tenant");
  }

  function abrirFormExtrairPrompts() {
    setFluxoSelecionado("prompts");
  }

  function atualizarResultadoPrompt(
    email: string,
    dados: Partial<ResultadoPrompt>
  ) {
    setResultadosPrompts((atuais) =>
      atuais.map((item) =>
        item.email === email ? { ...item, ...dados } : item
      )
    );
  }

  function executarCriarTenant() {
    if (!idMedico.trim() || !nomeMedico.trim()) {
      atualizarStatusTenant("finalizacao", "erro");
      return;
    }

    setCarregando("tenant");
    setStatusTenant(statusTenantInicial);

    const params = new URLSearchParams({
      id_medico: idMedico,
      nome_medico: nomeMedico,
    });

    const eventos = new EventSource(
      `${API_URL}/executar/criar-tenant-stream?${params.toString()}`
    );

    eventos.onmessage = (evento) => {
      const dados = JSON.parse(evento.data);

      if (dados.etapa && dados.status) {
        atualizarStatusTenant(dados.etapa, dados.status as Status);
      }
    };

    eventos.addEventListener("finalizado", () => {
      setCarregando("");
      eventos.close();
    });

    eventos.onerror = () => {
      atualizarStatusTenant("finalizacao", "erro");
      setCarregando("");
      eventos.close();
    };
  }

  async function executarExtrairPrompts() {
    const emails = emailsTexto
      .split(/\n|,|;/)
      .map((email) => email.trim())
      .filter(Boolean);

    if (emails.length === 0) {
      atualizarStatusPrompts("finalizacao", "erro");
      return;
    }

    setCarregando("prompts");
    setStatusPrompts(statusPromptsInicial);

    setResultadosPrompts(
      emails.map((email) => ({
        email,
        status: "pendente",
        quantidadePrompts: 0,
        mensagem: "Aguardando execução",
      }))
    );

    for (let i = 0; i < emails.length; i++) {
        const email = emails[i];

        atualizarResultadoPrompt(email, {
          status: "executando",
          mensagem: "Executando extração",
        });

        await new Promise<void>((resolve) => {
          const params = new URLSearchParams({
            email_medico: email,
            limpar_arquivo: i === 0 ? "true" : "false",
          });

          const eventos = new EventSource(
            `${API_URL}/executar/extrair-prompts-stream?${params.toString()}`
          );

        eventos.onmessage = (evento) => {
          const dados = JSON.parse(evento.data);

          if (dados.etapa && dados.status) {
            atualizarStatusPrompts(dados.etapa, dados.status as Status);
          }

          if (dados.etapa === "finalizacao") {
            const mensagem = dados.mensagem || "";
            const quantidade = dados.dados?.quantidade_prompts || 0;

            if (quantidade > 0) {
              atualizarResultadoPrompt(email, {
                status: "executado",
                quantidadePrompts: quantidade,
                mensagem: `Prompt extraído. Quantidade: ${quantidade}`,
              });
            } else if (
              mensagem.toLowerCase().includes("não foi possível realizar login") ||
              mensagem.toLowerCase().includes("nao foi possivel realizar login")
            ) {
              atualizarResultadoPrompt(email, {
                status: "executado",
                quantidadePrompts: 0,
                mensagem: "Não logou",
              });
            } else if (
              mensagem.toLowerCase().includes("não consegui extrair") ||
              mensagem.toLowerCase().includes("nao consegui extrair") ||
              mensagem.toLowerCase().includes("nenhum prompt")
            ) {
              atualizarResultadoPrompt(email, {
                status: "executado",
                quantidadePrompts: 0,
                mensagem: "Logou, mas não achou prompt",
              });
            }
          }
        };

        eventos.addEventListener("finalizado", () => {
          eventos.close();
          resolve();
        });

        eventos.onerror = () => {
          atualizarStatusPrompts("finalizacao", "erro");

          atualizarResultadoPrompt(email, {
            status: "executado",
            quantidadePrompts: 0,
            mensagem: "Erro durante a execução",
          });

          eventos.close();
          resolve();
        };
      });
    }

    setCarregando("");
  }

  async function executarCriarAgente() {
    setCarregando("agente");

    try {
      const resposta = await fetch(`${API_URL}/executar/criar-agente`, {
        method: "POST",
      });

      if (!resposta.ok) {
        throw new Error("Erro ao executar Criar Agente.");
      }
    } catch (erro) {
      console.error(erro);
    } finally {
      setCarregando("");
    }
  }

  function executarZarpon() {
    setCarregando("zarpon");
    setCarregando("");
  }

  return (
    <div className="flex h-screen overflow-hidden bg-black text-white">
      <Sidebar
        carregando={carregando}
        executarCriarTenant={abrirFormCriarTenant}
        executarCriarAgente={executarCriarAgente}
        executarZarpon={abrirFormExtrairPrompts}
      />

      <main className="h-screen flex-1 overflow-y-auto p-8">
        <header className="mb-8">
          <h2 className="text-3xl font-bold">Painel de Automação</h2>

          <p className="text-slate-400">
            Visão geral dos fluxos, agentes e execuções do sistema.
          </p>
        </header>

        {fluxoSelecionado === "tenant" && (
          <section className="mb-6 rounded-xl border border-slate-700/50 bg-slate-900 p-6">
            <h3 className="mb-4 text-xl font-bold">Criar Tenant</h3>

            <div className="grid gap-4 md:grid-cols-2">
              <input
                type="text"
                placeholder="Ex: #199"
                value={idMedico}
                onChange={(e) => setIdMedico(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 p-3 text-white outline-none focus:border-blue-500"
              />

              <input
                type="text"
                placeholder="Nome do médico"
                value={nomeMedico}
                onChange={(e) => setNomeMedico(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 p-3 text-white outline-none focus:border-blue-500"
              />
            </div>

            <button
              type="button"
              onClick={executarCriarTenant}
              disabled={carregando !== ""}
              className="mt-4 rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Executar Criar Tenant
            </button>

            <StatusPanel itens={statusTenant} tipo="tenant" />
          </section>
        )}

        {fluxoSelecionado === "prompts" && (
          <section className="mb-6 rounded-xl border border-slate-700/50 bg-slate-900 p-6">
            <h3 className="mb-4 text-xl font-bold">Extrair Prompts</h3>

            <textarea
              placeholder={`Digite um ou vários e-mails. Ex:\nmedico1@email.com\nmedico2@email.com`}
              value={emailsTexto}
              onChange={(e) => setEmailsTexto(e.target.value)}
              rows={6}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 p-3 text-white outline-none focus:border-blue-500"
            />

            <button
              type="button"
              onClick={executarExtrairPrompts}
              disabled={carregando !== ""}
              className="mt-4 rounded-lg bg-emerald-600 px-5 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Executar Extração de Prompts
            </button>

            <StatusPanel
              itens={statusPrompts}
              tipo="prompts"
              resultadosPrompts={resultadosPrompts}
            />
          </section>
        )}
      </main>
    </div>
  );
}