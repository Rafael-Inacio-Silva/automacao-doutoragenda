"use client";

import { useState } from "react";
import Sidebar from "../components/Sidebar";
import StatusPanel from "../components/StatusPanel";

export default function Page() {
  const [mensagem, setMensagem] = useState(
    "Selecione uma opção no menu lateral para executar uma automação."
  );

  const [carregando, setCarregando] = useState("");

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  async function executarCriarTenant() {
    setCarregando("tenant");
    setMensagem("Executando fluxo Criar Tenant...");

    try {
      const resposta = await fetch(`${API_URL}/executar/criar-tenant`, {
        method: "POST",
      });

      if (!resposta.ok) {
        throw new Error("Erro ao executar Criar Tenant.");
      }

      const dados = await resposta.json();

      setMensagem(
        dados?.resultado?.mensagem || "Fluxo Criar Tenant executado com sucesso."
      );
    } catch (erro) {
      console.error(erro);
      setMensagem("Erro ao conectar com o backend.");
    } finally {
      setCarregando("");
    }
  }

  async function executarCriarAgente() {
    setCarregando("agente");
    setMensagem("Executando fluxo Criar Agente...");

    try {
      const resposta = await fetch(`${API_URL}/executar/criar-agente`, {
        method: "POST",
      });

      if (!resposta.ok) {
        throw new Error("Erro ao executar Criar Agente.");
      }

      const dados = await resposta.json();

      setMensagem(
        dados?.resultado?.mensagem || "Fluxo Criar Agente executado com sucesso."
      );
    } catch (erro) {
      console.error(erro);
      setMensagem("Erro ao conectar com o backend.");
    } finally {
      setCarregando("");
    }
  }

  function executarZarpon() {
    setCarregando("zarpon");
    setMensagem("Fluxo Zarpon ainda não configurado.");
    setCarregando("");
  }

  return (
    <div className="flex h-screen overflow-hidden bg-black text-white">
      <Sidebar
        carregando={carregando}
        executarCriarTenant={executarCriarTenant}
        executarCriarAgente={executarCriarAgente}
        executarZarpon={executarZarpon}
      />

      <main className="h-screen flex-1 overflow-hidden p-8">
        <header className="mb-8">
          <h2 className="text-3xl font-bold">Painel de Automação</h2>

          <p className="text-slate-400">
            Visão geral dos fluxos, agentes e execuções do sistema.
          </p>
        </header>

        <StatusPanel mensagem={mensagem} />
      </main>
    </div>
  );
}