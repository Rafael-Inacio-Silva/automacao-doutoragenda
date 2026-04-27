type StatusPanelProps = {
  mensagem: string;
};

export default function StatusPanel({ mensagem }: StatusPanelProps) {
  return (
    <section className="mt-10 rounded-xl border border-slate-700/50 bg-slate-800/50 p-6">
      <h3 className="text-xl font-bold text-white">Status da Automação</h3>

      <p className="mt-2 text-sm text-slate-400">{mensagem}</p>
    </section>
  );
}