import Link from "next/link";

const actions = [
  { href: "/sobre", label: "Sobre", description: "Conheça a identidade e as possibilidades do Miyora.", mark: "01" },
  { href: "/dashboard", label: "Gerenciar", description: "Entre com o Discord e abra seus servidores.", mark: "02" },
  { href: "/adicionar", label: "Adicionar", description: "Convide o Miyora usando o fluxo oficial.", mark: "03" },
];

export default function HomePage() {
  return (
    <div className="site-shell">
      <header className="topbar">
        <Link className="brand" href="/" aria-label="Miyora início">
          <span className="brand-mark">M</span>
          <span>Miyora</span>
        </Link>
        <nav className="topnav" aria-label="Navegação principal">
          <Link href="/sobre">Sobre</Link>
          <Link href="/dashboard">Gerenciar</Link>
          <Link href="/adicionar">Adicionar</Link>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">Comunidade • Kawaii • Organização</p>
            <h1>Seu servidor com mais carinho e personalidade.</h1>
            <p className="hero-lead">
              O Miyora prepara a casa da sua comunidade no Discord, com uma experiência clara, acolhedora e feita para crescer.
            </p>
            <div className="hero-actions">
              {actions.map((action) => (
                <Link className="action-link" href={action.href} key={action.label}>
                  <span className="action-mark">{action.mark}</span>
                  <span><strong>{action.label}</strong><small>{action.description}</small></span>
                  <span aria-hidden="true">→</span>
                </Link>
              ))}
            </div>
          </div>
          <div className="miyora-spot" aria-label="Símbolo visual Miyora">
            <div className="ribbon ribbon-one" />
            <div className="ribbon ribbon-two" />
            <div className="miyora-seal"><span>M</span></div>
            <p>Minha missão é cuidar da sua comunidade.</p>
          </div>
        </section>
      </main>

      <footer className="footer">
        <span>Miyora</span>
        <nav aria-label="Links relevantes">
          <Link href="/sobre">Sobre</Link>
          <Link href="/status">Status</Link>
          <Link href="/dashboard">Painel</Link>
        </nav>
      </footer>
    </div>
  );
}
