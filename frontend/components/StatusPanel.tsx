type Status = "pendente" | "executando" | "concluido" | "erro" | "alerta";

type ChecklistItem = {
  etapa: string;
  titulo: string;
  status: Status;
};

type ResultadoPrompt = {
  email: string;
  status:
    | "pendente"
    | "executando"
    | "com_prompt"
    | "nao_logou"
    | "sem_prompt"
    | "erro";
  quantidadePrompts: number;
  mensagem: string;
};

type StatusPanelProps = {
  itens: ChecklistItem[];
  resultadosPrompts?: ResultadoPrompt[];
  tipo?: "tenant" | "prompts";
};

const statusConfig = {
  pendente: {
    simbolo: "○",
    texto: "Pendente",
    classe: "text-slate-500",
  },
  executando: {
    simbolo: "◔",
    texto: "Em andamento",
    classe: "text-blue-400",
  },
  concluido: {
    simbolo: "●",
    texto: "Concluído",
    classe: "text-emerald-400",
  },
  erro: {
    simbolo: "●",
    texto: "Erro",
    classe: "text-red-400",
  },
  alerta: {
    simbolo: "●",
    texto: "Atenção",
    classe: "text-yellow-400",
  },
};

function textoStatusPrompt(status: ResultadoPrompt["status"]) {
  if (status === "executado") return "Executado";
  if (status === "executando") return "Executando";
  return "Pendente";
}

function classeStatusPrompt(status: ResultadoPrompt["status"]) {
  if (status === "executado") return "text-emerald-400";
  if (status === "executando") return "text-blue-400";
  return "text-slate-400";
}

export default function StatusPanel({
  itens,
  resultadosPrompts = [],
  tipo = "tenant",
}: StatusPanelProps) {
  const etapaFinalizacao = itens.find((item) => item.etapa === "finalizacao");

  const execucaoFinalizada =
    etapaFinalizacao?.status === "concluido" ||
    etapaFinalizacao?.status === "erro";

  function baixarArquivoResultado() {
    if (tipo === "tenant") {
      window.open("http://127.0.0.1:8000/download/tenant", "_blank");
      return;
    }

    window.open("http://127.0.0.1:8000/download/prompts", "_blank");
  }

  function baixarArquivoLog() {
    if (tipo === "tenant") {
      window.open("http://127.0.0.1:8000/download/log-tenant", "_blank");
      return;
    }

    window.open("http://127.0.0.1:8000/download/log-prompts", "_blank");
  }

  return (
    <section className="mt-6 w-full rounded-xl border border-slate-700/50 bg-slate-800/50 p-4 sm:p-6">
      <aside className="flex w-full flex-col rounded-lg border border-slate-800 bg-[#06111f] p-4 sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h3 className="text-lg font-bold text-white sm:text-xl">
            Status da Automação
          </h3>

          {execucaoFinalizada && (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={baixarArquivoResultado}
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700 bg-slate-900 text-slate-200 transition hover:bg-slate-800 hover:text-white"
                title={tipo === "tenant" ? "Baixar resultado do tenant" : "Baixar arquivo de prompts"}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                  aria-hidden="true"
                >
                  <path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z" />
                  <path d="M14 2v5a1 1 0 0 0 1 1h5" />
                  <path d="M12 18v-6" />
                  <path d="m9 15 3 3 3-3" />
                </svg>
              </button>

              <button
                type="button"
                onClick={baixarArquivoLog}
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-700 bg-slate-900 text-slate-200 transition hover:bg-slate-800 hover:text-white"
                title={tipo === "tenant" ? "Baixar log do tenant" : "Baixar log da extração"}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                  aria-hidden="true"
                >
                  <path d="M15 12h-5" />
                  <path d="M15 8h-5" />
                  <path d="M19 17V5a2 2 0 0 0-2-2H4" />
                  <path d="M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3" />
                </svg>
              </button>
            </div>
          )}
        </div>

        <div className="mt-5 space-y-3">
          {tipo === "prompts" ? (
            resultadosPrompts.length > 0 ? (
              <>
                <div className="grid grid-cols-1 gap-3 px-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500 md:grid-cols-3">
                  <span>Email</span>
                  <span>Status</span>
                  <span>Mensagem</span>
                </div>

                {resultadosPrompts.map((item) => (
                <div
                  key={item.email}
                  className="grid grid-cols-1 gap-3 rounded-lg border border-slate-800 bg-black/20 px-4 py-3 text-left md:grid-cols-3 md:items-start"
                >
                  <span className="text-slate-200">{item.email}</span>

                  <span
                    className={`font-medium ${classeStatusPrompt(
                      item.status
                    )}`}
                  >
                    {textoStatusPrompt(item.status)}
                  </span>

                  <span className="text-slate-400">{item.mensagem}</span>
                </div>
              ))}
              </>
            ) : (
              <div className="rounded-lg border border-slate-800 bg-black/20 px-4 py-3 text-slate-400">

              </div>
            )
          ) : (
            itens.map((item) => {
              const config = statusConfig[item.status];

              return (
                <div
                  key={item.etapa}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-black/20 px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className={`text-lg ${config.classe}`}>
                      {config.simbolo}
                    </span>

                    <span className="text-sm text-slate-200 sm:text-base">
                      {item.titulo}
                    </span>
                  </div>

                  <span
                    className={`text-xs font-medium sm:text-sm ${config.classe}`}
                  >
                    {config.texto}
                  </span>
                </div>
              );
            })
          )}
        </div>
      </aside>
    </section>
  );
}