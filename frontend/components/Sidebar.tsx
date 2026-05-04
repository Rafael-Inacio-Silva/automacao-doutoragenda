"use client";

import Image from "next/image";
import Button from "./button";

type SidebarProps = {
  carregando: string;
  executarTestarAgente: () => void;
  executarCriarTenant: () => void;
  executarCriarAgente: () => void;
  executarZarpon: () => void;
};

export default function Sidebar({
  carregando,
  executarTestarAgente,
  executarCriarTenant,
  executarCriarAgente,
  executarZarpon,
}: SidebarProps) {
  return (
    <aside className="flex h-screen w-73 shrink-0 flex-col bg-[#06111f] border-r border-slate-800 p-6">
      <div className="mb-10 flex items-center gap-3">
        <Image
          src="/automacao_verde.png"
          alt="Logo Automação"
          width={80}
          height={80}
        />

        <div>
          <h1 className="text-2xl font-bold flex w-full items-center justify-center gap-3 rounded-xl px-4 py-3 text-slate-300 transition">
            Automação
          </h1>
        </div>
      </div>

      <nav className="mt-auto w-full rounded-xl border border-slate-700/50 bg-slate-800/50">
        <Button
          quandoClica={executarTestarAgente}
          ativo={carregando === "qa"}
          disabled={carregando !== ""}
        >
          <div className="flex items-center justify-start gap-3">

            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
            >
              <path d="M10 19.655A6 6 0 0 1 6 14v-3a4 4 0 0 1 4-4h4a4 4 0 0 1 4 3.97"/>
              <path d="M14 15.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997a1 1 0 0 1-1.517-.86z"/>
              <path d="M14.12 3.88 16 2"/>
              <path d="M21 5a4 4 0 0 1-3.55 3.97"/>
              <path d="M3 21a4 4 0 0 1 3.81-4"/>
              <path d="M3 5a4 4 0 0 0 3.55 3.97"/>
              <path d="M6 13H2"/>
              <path d="m8 2 1.88 1.88"/>
              <path d="M9 7.13V6a3 3 0 1 1 6 0v1.13"/>
            </svg>

            <span>{carregando === "qa" ? "Executando..." : "Testar Agente"}</span>
          </div>
        </Button>

        <Button
          quandoClica={executarCriarTenant}
          ativo={carregando === "tenant"}
          disabled={carregando !== ""}
        >
          <div className="flex items-center justify-start gap-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" />
              <path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2" />
              <path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2" />
              <path d="M10 6h4" />
              <path d="M10 10h4" />
              <path d="M10 14h4" />
              <path d="M10 18h4" />
            </svg>

            <span>
              {carregando === "tenant" ? "Executando..." : "Criar Tenant"}
            </span>
          </div>
        </Button>

        <Button
          quandoClica={executarCriarAgente}
          ativo={carregando === "agente"}
          disabled={carregando !== ""}
        >
          <div className="flex items-center justify-start gap-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path d="M12 8V4H8" />
              <rect width="16" height="12" x="4" y="8" rx="2" />
              <path d="M2 14h2" />
              <path d="M20 14h2" />
              <path d="M15 13v2" />
              <path d="M9 13v2" />
            </svg>

            <span>
              {carregando === "agente" ? "Executando..." : "Criar Agente"}
            </span>
          </div>
        </Button>

        <Button
          quandoClica={executarZarpon}
          ativo={carregando === "zarpon"}
          disabled={carregando !== ""}
        >
          <div className="flex items-center justify-start gap-3">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path stroke="none" d="M0 0h24v24H0z" fill="none" />
              <path d="M12 18.004h-5.343c-2.572-.004-4.657-2.011-4.657-4.487c0-2.475 2.085-4.482 4.657-4.482c.393-1.762 1.794-3.2 3.675-3.773c1.88-.572 3.956-.193 5.444 1c1.488 1.19 2.162 3.007 1.77 4.769h.99c1.38 0 2.573.813 3.13 1.99" />
              <path d="M19 16v6" />
              <path d="M22 19l-3 3-3-3" />
            </svg>

            <span>Extrair Prompts</span>
          </div>
        </Button>
      </nav>

      <nav className="mt-20 h-94 w-full rounded-xl border border-slate-700/50 bg-slate-800/50"></nav>

      <nav className="mt-10 w-full rounded-2xl border border-slate-700/50 bg-slate-800/40 px-4 py-4 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-0">
            <div className="-ml-4 flex h-10 w-10 rounded-full">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-9 w-9 text-slate-300"
              >
                <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>

            <div>
              <div className="flex items-center gap-3">
                <p className="p-1 text-sm font-semibold text-slate-200">
                  Ambiente Seguro
                </p>

                <button
                  type="button"
                  className="ml-8 relative flex h-3 w-3 items-center justify-center"
                  aria-label="Sistema operacional"
                >
                  <span className="absolute inline-flex h-full w-full animate-[ping_2s_cubic-bezier(0,0,0.2,1)_infinite] rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex h-3 w-3 rounded-full bg-emerald-400"></span>
                </button>
              </div>

              <p className="p-1 -ml-2 justify-between text-xs text-slate-400">
                Dados protegidos e criptografados
              </p>
            </div>
          </div>
        </div>
      </nav>
    </aside>
  );
}