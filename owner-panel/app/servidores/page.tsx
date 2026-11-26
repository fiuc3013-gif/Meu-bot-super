import { cookies } from "next/headers";
import { verifyOwnerSession } from "../../lib/auth";
import { callBotAdmin } from "../../lib/bot-client";
import { AdminShell } from "../../components/admin-shell";

export const dynamic = "force-dynamic";

export default async function ServersPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const session = verifyOwnerSession((await cookies()).get("miyora_owner_session")?.value);
  if (!session) return <main className="login-screen"><a className="primary-button" href="/api/auth/discord">Entrar</a></main>;
  const query = (await searchParams).q?.trim().toLowerCase() ?? "";
  let guilds: Array<{ guild_id: string; name: string; member_count: number | null }> = [];
  try { guilds = (await callBotAdmin("/guilds") as { guilds: typeof guilds }).guilds; } catch {}
  const filtered = guilds.filter((guild) => guild.name.toLowerCase().includes(query) || guild.guild_id.includes(query));

  return (
    <AdminShell title="Servidores" eyebrow="Gerenciamento global" active="/servidores">
      <form className="search-row"><input name="q" defaultValue={query} placeholder="Pesquisar nome ou ID" /><button className="primary-button" type="submit">Pesquisar</button></form>
      <section className="table-panel">
        <table><thead><tr><th>Servidor</th><th>ID</th><th>Membros</th><th>Estado</th></tr></thead>
          <tbody>{filtered.map((guild) => <tr key={guild.guild_id}><td>{guild.name}</td><td>{guild.guild_id}</td><td>{guild.member_count ?? "Não disponível"}</td><td>Conectado</td></tr>)}</tbody>
        </table>
        {filtered.length === 0 && <p className="notice">Nenhum servidor foi retornado pela API ou não há correspondência na pesquisa.</p>}
      </section>
    </AdminShell>
  );
}
