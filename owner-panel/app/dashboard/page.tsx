import { cookies } from "next/headers";
import { verifyOwnerSession } from "../../lib/auth";
import { callBotAdmin } from "../../lib/bot-client";
import { AdminShell } from "../../components/admin-shell";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const session = verifyOwnerSession((await cookies()).get("miyora_owner_session")?.value);
  if (!session) return <main className="login-screen"><section className="login-card"><p className="eyebrow">Acesso privado</p><h1>Entre como proprietário</h1><p>Este painel somente aceita o Discord User ID configurado.</p><a className="primary-button" href="/api/auth/discord">Entrar com Discord</a></section></main>;

  let stats: { guild_count: number; member_count: number; future_modules: string[] } = { guild_count: 0, member_count: 0, future_modules: [] };
  let economy: { implemented: boolean; guild_count: number; total_balance: number } = { implemented: false, guild_count: 0, total_balance: 0 };
  let bot: { name: string; bot_connected: boolean } = { name: "Miyora", bot_connected: false };
  try { stats = await callBotAdmin("/stats"); } catch {}
  try { economy = await callBotAdmin("/economy"); } catch {}
  try { bot = await callBotAdmin("/info"); } catch {}

  const cards = [
    ["Servidores", stats.guild_count], ["Membros", stats.member_count], ["Estado do bot", bot.bot_connected ? "Conectado" : "Indisponível"], ["Economia", economy.implemented ? economy.total_balance : "Não implementada"],
  ];

  return (
    <AdminShell title="Visão global" eyebrow="Central Miyora" active="/dashboard">
      <section className="panel-grid">{cards.map(([label, value]) => <article className="stat-card" key={String(label)}><span>{label}</span><strong>{value}</strong></article>)}</section>
      <section className="table-panel"><h2>Atividades administrativas</h2><table><thead><tr><th>Fonte</th><th>Estado</th></tr></thead><tbody><tr><td>API administrativa</td><td>{bot.bot_connected ? "Disponível" : "Aguardando conexão"}</td></tr><tr><td>Economia global</td><td>{economy.implemented ? "Disponível" : "Aguardando módulos futuros"}</td></tr></tbody></table></section>
    </AdminShell>
  );
}
