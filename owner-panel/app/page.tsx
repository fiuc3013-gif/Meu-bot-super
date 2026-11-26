import Link from "next/link";

export default function OwnerPage() {
  return (
    <main className="login-screen">
      <section className="login-card">
        <span className="brand-mark">M</span>
        <p className="eyebrow">Central Miyora</p>
        <h1>Área privada do proprietário</h1>
        <p>Autenticação exclusiva pelo Discord configurado no ambiente administrativo.</p>
        <a className="primary-button" href="/api/auth/discord">Entrar com Discord</a>
        <Link className="text-link" href="/api/health">Verificar status da API</Link>
      </section>
    </main>
  );
}
