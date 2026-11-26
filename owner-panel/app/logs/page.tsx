import { cookies } from "next/headers";
import { verifyOwnerSession } from "../../lib/auth";
import { AdminShell } from "../../components/admin-shell";
import { callBotAdmin } from "../../lib/bot-client";

export const dynamic = "force-dynamic";

export default async function LogsPage() {
  const session = verifyOwnerSession((await cookies()).get("miyora_owner_session")?.value);
  if (!session) return <main className="login-screen"><a className="primary-button" href="/api/auth/discord">Entrar</a></main>;
  let logs: Array<{ id: number; administrator_id: string; action: string; entity_type: string; reason: string; created_at: string }> = [];
  try { logs = (await callBotAdmin("/audit") as { logs: typeof logs }).logs; } catch {}
  return (
    <AdminShell title="Logs e auditoria" eyebrow="Histórico administrativo" active="/logs">
      <section className="table-panel"><table><thead><tr><th>Ação</th><th>Responsável</th><th>Data</th><th>Motivo</th></tr></thead><tbody>{logs.length ? logs.map((log) => <tr key={log.id}><td>{log.action}</td><td>{log.administrator_id}</td><td>{log.created_at}</td><td>{log.reason}</td></tr>) : <tr><td colSpan={4}>Nenhum registro disponível.</td></tr>}</tbody></table></section>
    </AdminShell>
  );
}
