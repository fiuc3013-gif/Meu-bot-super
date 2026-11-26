import { cookies } from "next/headers";
import { verifyOwnerSession } from "../../lib/auth";
import { AdminShell } from "../../components/admin-shell";
import { callBotAdmin } from "../../lib/bot-client";

export const dynamic = "force-dynamic";

export default async function MembersPage({ searchParams }: { searchParams: Promise<{ memberId?: string }> }) {
  const session = verifyOwnerSession((await cookies()).get("miyora_owner_session")?.value);
  if (!session) return <main className="login-screen"><a className="primary-button" href="/api/auth/discord">Entrar</a></main>;
  const memberId = (await searchParams).memberId?.trim() ?? "";
  let member: { member_id: string; guilds: Array<{ guild_id: string; guild_name: string; display_name: string }> } | null = null;
  let error = "";
  if (/^\d+$/.test(memberId)) {
    try { member = await callBotAdmin(`/members/${memberId}`) as { member_id: string; guilds: Array<{ guild_id: string; guild_name: string; display_name: string }> }; } catch { error = "Membro não encontrado ou API indisponível."; }
  }
  return (
    <AdminShell title="Membros" eyebrow="Gerenciamento administrativo" active="/membros">
      <form className="search-row"><input name="memberId" defaultValue={memberId} placeholder="Discord User ID" pattern="[0-9]+" /><button className="primary-button" type="submit">Consultar</button></form>
      {error && <p className="notice">{error}</p>}
      {member && <section className="table-panel"><table><thead><tr><th>ID</th><th>Servidor</th><th>Nome</th></tr></thead><tbody>{member.guilds.map((guild) => <tr key={guild.guild_id}><td>{member?.member_id}</td><td>{guild.guild_name}</td><td>{guild.display_name}</td></tr>)}</tbody></table></section>}
      <div className="category-grid">
        <article className="category-card"><h2>Carteira e banco</h2><p>Disponível após o módulo de economia unificada.</p></article>
        <article className="category-card disabled"><h2>Transações</h2><p>Nenhum histórico foi fornecido pela API atual.</p></article>
        <article className="category-card disabled"><h2>Alteração de saldo</h2><p>Exige endpoint econômico, motivo, administrador e auditoria. Não disponível nesta etapa.</p></article>
      </div>
      <div className="confirmation"><strong>Proteção de ações críticas</strong><p>Qualquer alteração futura exigirá confirmação, motivo e registro do proprietário responsável.</p></div>
    </AdminShell>
  );
}
