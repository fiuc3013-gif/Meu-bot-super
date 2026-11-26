import Link from "next/link";

export default function AddPage() {
  const clientId = process.env.DISCORD_CLIENT_ID;
  const inviteUrl = process.env.DISCORD_INVITE_URL;
  const fallback = clientId
    ? `https://discord.com/api/oauth2/authorize?client_id=${encodeURIComponent(clientId)}&permissions=3072&scope=bot%20applications.commands`
    : null;
  const url = inviteUrl || fallback;

  return (
    <div className="site-shell">
      <header className="topbar"><Link className="brand" href="/"><span className="brand-mark">M</span><span>Miyora</span></Link><nav className="topnav"><Link href="/sobre">Sobre</Link><Link href="/dashboard">Gerenciar</Link></nav></header>
      <main className="content-page"><div className="empty-state">
        <p className="eyebrow">Convite oficial</p><h1>Adicione o Miyora ao seu servidor</h1>
        <p>O link solicita apenas permissões básicas necessárias para presença e respostas. O conjunto pode crescer somente em etapas futuras autorizadas.</p>
        {url ? <a className="primary-button" href={url}>Abrir convite no Discord</a> : <p className="notice">Configure `DISCORD_CLIENT_ID` ou `DISCORD_INVITE_URL` no ambiente Vercel.</p>}
      </div></main>
    </div>
  );
}
