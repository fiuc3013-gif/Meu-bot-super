import Link from "next/link";
import { cookies } from "next/headers";
import { verifyPublicSession } from "../../../lib/auth";
import { GuildConfigPanel } from "../../../components/guild-config-panel";

export const dynamic = "force-dynamic";

const categories = [
  "Geral",
  "Boas-vindas e despedidas",
  "Moderação",
  "XP e níveis",
  "Economia",
  "Loja",
  "Tickets",
  "Sorteios",
  "Avaliações",
  "Cargos automáticos",
  "Mensagens automáticas",
  "Logs",
  "Utilidades",
];

export default async function GuildDashboard({ params }: { params: Promise<{ guildId: string }> }) {
  const { guildId } = await params;
  if (!/^\d+$/.test(guildId)) {
    return <main className="content-page"><div className="empty-state"><h1>Servidor inválido</h1><p>O identificador informado não é válido.</p></div></main>;
  }

  const session = verifyPublicSession((await cookies()).get("miyora_session")?.value);
  if (!session) {
    return <main className="content-page"><div className="empty-state"><h1>Faça login novamente</h1><a className="primary-button" href="/api/auth/discord">Entrar com Discord</a></div></main>;
  }
  if (!session.guildIds.includes(guildId)) {
    return <main className="content-page"><div className="empty-state"><h1>Acesso negado</h1><p>Você não possui permissão para gerenciar este servidor.</p><Link className="primary-button" href="/dashboard">Voltar aos servidores</Link></div></main>;
  }

  const guild = session.guilds.find((item) => item.id === guildId);
  return (
    <div className="site-shell">
      <header className="topbar"><Link className="brand" href="/"><span className="brand-mark">M</span><span>Miyora</span></Link><nav className="topnav"><Link href="/dashboard">Servidores</Link></nav></header>
      <main className="content-page">
        <div className="page-heading"><div><p className="eyebrow">Gerenciamento</p><h1>{guild?.name || guildId}</h1></div><Link className="secondary-button" href="/dashboard">Voltar</Link></div>
        <div className="settings-layout">
          <aside className="settings-nav" aria-label="Categorias de configuração">{categories.map((category) => <a key={category}>{category}</a>)}</aside>
          <GuildConfigPanel guildId={guildId} />
        </div>
      </main>
    </div>
  );
}
