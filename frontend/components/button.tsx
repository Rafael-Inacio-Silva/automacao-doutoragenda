"use client";

import type { ReactNode } from "react";

type ButtonProps = {
  children: ReactNode;
  quandoClica?: () => void;
  ativo?: boolean;
  disabled?: boolean;
};

export default function Button({
  children,
  quandoClica,
  ativo = false,
  disabled = false,
}: ButtonProps) {
  return (
    <button
      type="button"
      onClick={quandoClica}
      disabled={disabled}
      className={`w-full rounded-xl px-4 py-3 text-left transition cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 ${
        ativo
          ? "bg-blue-500/30 text-white"
          : "text-slate-300 hover:bg-slate-800 hover:text-white"
      }`}
    >
      {children}
    </button>
  );
}