import Link from "next/link";

export default function StatusPage() {
  return (
    <div className="site-shell">
      <header className="topbar"><Link className="brand" href="/"><span className="brand-mark">M</span><span>Miyora</span></Link></header>
      <main className="content-page"><div className="empty-state"><p className="eyebrow">Status</p><h1>Estado do serviço</h1><p>O estado em tempo real depende da API do bot configurada na Wispbyte.</p><Link className="primary-button" href="/dashboard">Consultar painel</Link></div></main>
    </div>
  );
}
