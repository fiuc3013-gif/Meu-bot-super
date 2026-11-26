import Link from "next/link";
import { cookies } from "next/headers";
import { verifyPublicSession } from "../../lib/auth";
import { callBot } from "../../lib/bot-client";
import { LogoutButton } from "../../components/logout-button";
import { ThemeToggle } from "../../components/theme-toggle";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const session = verifyPublicSession(cookieStore.get("miyora_session")?.value);

  if (!session) {
    return (
      <div className="site-shell"><header className="topbar"><Link className="brand" href="/"><span className="brand-mark">M</span><span>Miyora</span></Link></header>
        <main className="content-page"><div className="empty-state"><p className="eyebrow">Gerenciar</p><h1>Entre com o Discord</h1><p>Entre para ver apenas os servidores em que você pode gerenciar o Miyora.</p><a className="primary-button" href="/api/auth/discord">Continuar com Discord</a></div></main>
      </div>
    );
  }

  let botGuildIds = new Set<string>();
  try {
    const data = await callBot("/api/v1/guilds") as { guilds: Array<{ guild_id: string }> };
    botGuildIds = new Set(data.guilds.map((guild) => guild.guild_id));
  } catch {}

  return (
    <div className="site-shell">
      <header className="topbar"><Link className="brand" href="/"><span className="brand-mark">M</span><span>Miyora</span></Link><nav className="topnav"><span>{session.user.username}</span></nav></header>
      <main className="content-page">
        <div className="page-heading"><div><p className="eyebrow">Painel público</p><h1>Servidores</h1></div><div style={{ display: "flex", gap: 8 }}><ThemeToggle /><LogoutButton /></div></div>
        {session.guilds.length === 0 ? (
          <div className="empty-state"><h2>Nenhum servidor disponível</h2><p>Você precisa ser proprietário ou possuir Gerenciar Servidor em pelo menos um servidor.</p></div>
        ) : (
          <div className="guild-grid">
            {session.guilds.map((guild) => (
              <article className="guild-card" key={guild.id}>
                <div className="guild-card-head">
                  {guild.icon ? <img className="guild-icon" src={`https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png`} alt="" /> : <div className="guild-icon guild-fallback">M</div>}
                  <h2>{guild.name}</h2>
                </div>
                <p className="guild-state">Estado do Miyora: {botGuildIds.has(guild.id) ? "Conectado" : "Não encontrado"}</p>
                <Link className="primary-button" href={`/dashboard/${guild.id}`}>Abrir gerenciamento</Link>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
