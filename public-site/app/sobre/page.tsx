import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="site-shell">
      <header className="topbar"><Link className="brand" href="/"><span className="brand-mark">M</span><span>Miyora</span></Link><nav className="topnav"><Link href="/dashboard">Gerenciar</Link><Link href="/adicionar">Adicionar</Link></nav></header>
      <main className="content-page">
        <div className="page-heading"><div><p className="eyebrow">Sobre o Miyora</p><h1>Uma comunidade começa com cuidado.</h1></div></div>
        <section className="settings-layout">
          <aside className="settings-nav"><a>Identidade</a><a>Comunidade</a><a>Organização</a></aside>
          <article className="settings-panel">
            <h2>Miyora para o seu servidor</h2>
            <p>O Miyora prepara uma base organizada para comunidades no Discord. Nesta etapa, o site apresenta o projeto e permite gerenciar apenas as configurações já disponíveis pela API.</p>
            <div className="notice">Economia, XP, moderação completa, tickets e sorteios serão apresentados em etapas futuras.</div>
            <div className="hero-actions"><Link className="primary-button" href="/dashboard">Entrar no gerenciamento</Link><Link className="secondary-button" href="/adicionar">Adicionar ao Discord</Link></div>
          </article>
        </section>
      </main>
    </div>
  );
}
