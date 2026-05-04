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

type StatusRegraQA = "pendente" | "executando" | "aprovado" | "reprovado" | "erro";

type RegraQA = {
  titulo: string;
  status: StatusRegraQA;
  mensagem?: string;
};

type ResultadoQA = {
  tenant: string;
  status: "pendente" | "executando" | "aprovado" | "reprovado" | "erro";
  regras: RegraQA[];
  mensagem?: string;
};

const statusQAInicial: ChecklistItem[] = [
  { etapa: "execucao", titulo: "Executar teste QA", status: "pendente" },
  { etapa: "finalizacao", titulo: "Finalizar teste QA", status: "pendente" },
];

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
  const [fluxoSelecionado, setFluxoSelecionado] = useState<"tenant" | "prompts" | "qa" | null>(null);

  const [statusTenant, setStatusTenant] = useState<ChecklistItem[]>(statusTenantInicial);
  const [statusPrompts, setStatusPrompts] = useState<ChecklistItem[]>(statusPromptsInicial);

  const [idMedico, setIdMedico] = useState("");
  const [nomeMedico, setNomeMedico] = useState("");

  const [emailsTexto, setEmailsTexto] = useState("");
  const [resultadosPrompts, setResultadosPrompts] = useState<ResultadoPrompt[]>([]);

  const [tenantsTextoQA, setTenantsTextoQA] = useState("");
  const [statusQA, setStatusQA] = useState<ChecklistItem[]>(statusQAInicial);
  const [resultadosQA, setResultadosQA] = useState<ResultadoQA[]>([]);

  const regrasQAPadrao: RegraQA[] = [
  {
    titulo: "Regra 1 — Tenant 100% igual",
    status: "pendente",
  },
  {
    titulo: "Regra 2 — Sumarização de Contexto false",
    status: "pendente",
  },
  {
    titulo: "Regra 3 — Estágios obrigatórios",
    status: "pendente",
  },
  {
    titulo: "Regra 4 — Agendamento com buscar_proximos_horarios",
    status: "pendente",
  },
];

function abrirFormTestarAgente() {
  setFluxoSelecionado("qa");
}

function normalizarStatusAutomacao(status: string): Status {
  if (status === "executando") return "executando";
  if (status === "executado") return "concluido";
  if (status === "concluido") return "concluido";
  if (status === "erro") return "erro";
  if (status === "alerta") return "alerta";
  return "pendente";
}

function atualizarStatusQA(etapa: string, status: Status) {
  setStatusQA((itensAtuais) =>
    itensAtuais.map((item) =>
      item.etapa === etapa ? { ...item, status } : item
    )
  );
}

function normalizarTenantsQA(texto: string) {
  return texto
    .split(/\n/)
    .map((linha) => linha.trim())
    .filter(Boolean)
    .map((tenant) => {
      if (!tenant.startsWith("#")) {
        return `#${tenant}`;
      }

      return tenant;
    });
}

function criarResultadoQAInicial(tenant: string): ResultadoQA {
  return {
    tenant,
    status: "pendente",
    regras: regrasQAPadrao.map((regra) => ({ ...regra })),
  };
}

function atualizarResultadoQA(
  tenant: string,
  atualizacao: Partial<ResultadoQA>
) {
  setResultadosQA((atuais) =>
    atuais.map((item) =>
      item.tenant === tenant ? { ...item, ...atualizacao } : item
    )
  );
}

function atualizarRegraQA(
  tenant: string,
  indiceRegra: number,
  status: StatusRegraQA,
  mensagem?: string
) {
  setResultadosQA((atuais) =>
    atuais.map((item) => {
      if (item.tenant !== tenant) return item;

      const regrasAtualizadas = item.regras.map((regra, indice) => {
        if (indice !== indiceRegra) return regra;

        return {
          ...regra,
          status,
          mensagem,
        };
      });

      const temErro = regrasAtualizadas.some(
        (regra) => regra.status === "erro"
      );

      const temReprovado = regrasAtualizadas.some(
        (regra) => regra.status === "reprovado"
      );

      const todasExecutadas = regrasAtualizadas.every(
        (regra) =>
          regra.status === "aprovado" ||
          regra.status === "reprovado" ||
          regra.status === "erro"
      );

      let statusGeral: ResultadoQA["status"] = item.status;

      if (temErro) {
        statusGeral = "erro";
      } else if (temReprovado) {
        statusGeral = "reprovado";
      } else if (todasExecutadas) {
        statusGeral = "aprovado";
      } else {
        statusGeral = "executando";
      }

      return {
        ...item,
        status: statusGeral,
        regras: regrasAtualizadas,
      };
    })
  );
}

function normalizarStatusRegraQA(status: string): StatusRegraQA {
  if (status === "aprovado") return "aprovado";
  if (status === "reprovado") return "reprovado";
  if (status === "erro") return "erro";
  if (status === "executando") return "executando";
  return "pendente";
}

function executarTestarAgentesQA() {
  const tenants = normalizarTenantsQA(tenantsTextoQA);

  if (tenants.length === 0) {
    atualizarStatusQA("finalizacao", "erro");
    return;
  }

  setCarregando("qa");
  setStatusQA(statusQAInicial);

  setResultadosQA(tenants.map((tenant) => criarResultadoQAInicial(tenant)));

  atualizarStatusQA("execucao", "executando");

  const params = new URLSearchParams({
    tenants: tenants.join("\n"),
    limpar_arquivo: "true",
  });

  const eventos = new EventSource(
    `${API_URL}/executar/testar-agentes-qa-stream?${params.toString()}`
  );

  eventos.onmessage = (evento) => {
    const dados = JSON.parse(evento.data);

    const etapa = dados.etapa;
    const status = dados.status;
    const dadosInternos = dados.dados || {};
    const tenant = dadosInternos.tenant_teste;

    if (etapa === "inicio_item" && tenant) {
      atualizarResultadoQA(tenant, {
        status: "executando",
        mensagem: dados.mensagem,
      });
    }

    if (etapa === "regra_1" && tenant) {
      atualizarRegraQA(
        tenant,
        0,
        normalizarStatusRegraQA(dadosInternos.status),
        dadosInternos.mensagem
      );
    }

    if (etapa === "regra_2" && tenant) {
      atualizarRegraQA(
        tenant,
        1,
        normalizarStatusRegraQA(dadosInternos.status),
        dadosInternos.mensagem
      );
    }

    if (etapa === "regra_3" && tenant) {
      atualizarRegraQA(
        tenant,
        2,
        normalizarStatusRegraQA(dadosInternos.status),
        dadosInternos.mensagem
      );
    }

    if (etapa === "regra_4" && tenant) {
      atualizarRegraQA(
        tenant,
        3,
        normalizarStatusRegraQA(dadosInternos.status),
        dadosInternos.mensagem
      );
    }

    if (etapa === "fim_item" && tenant) {
      atualizarResultadoQA(tenant, {
        status: normalizarStatusRegraQA(
          dadosInternos.status_geral
        ) as ResultadoQA["status"],
        mensagem: dados.mensagem,
      });
    }

    if (etapa === "finalizacao" || etapa === "finalizacao_lote") {
      atualizarStatusQA("execucao", "concluido");
      atualizarStatusQA("finalizacao", normalizarStatusAutomacao(status));
    }
  };

  eventos.addEventListener("finalizado", () => {
    atualizarStatusQA("execucao", "concluido");
    atualizarStatusQA("finalizacao", "concluido");

    setCarregando("");
    eventos.close();
  });

  eventos.onerror = () => {
    atualizarStatusQA("finalizacao", "erro");

    setCarregando("");
    eventos.close();
  };
}

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
        executarTestarAgente={abrirFormTestarAgente}
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
        {fluxoSelecionado === "qa" && (
          <section className="mb-6 rounded-xl border border-slate-700/50 bg-slate-900 p-6">
            <h3 className="mb-4 text-xl font-bold">Testar Agente QA</h3>

            <textarea
              placeholder={`Digite um ou vários tenants. Ex:\n#586 - Dr. Raphael Palomares Jacobs\n#267 - Dra. Maria Teste`}
              value={tenantsTextoQA}
              onChange={(e) => setTenantsTextoQA(e.target.value)}
              rows={6}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 p-3 text-white outline-none focus:border-blue-500"
            />

            <button
              type="button"
              onClick={executarTestarAgentesQA}
              disabled={carregando !== ""}
              className="mt-4 rounded-lg bg-violet-600 px-5 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              Executar Teste QA
            </button>

            <StatusPanel
              itens={statusQA}
              tipo="qa"
              resultadosQA={resultadosQA}
            />
          </section>
        )}
      </main>
    </div>
  );
}