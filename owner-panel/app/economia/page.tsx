import { cookies } from "next/headers";
import { verifyOwnerSession } from "../../lib/auth";
import { callBotAdmin } from "../../lib/bot-client";
import { AdminShell } from "../../components/admin-shell";
import { EconomyAdmin } from "../../components/economy-admin";

export const dynamic = "force-dynamic";

export default async function EconomyPage() {
  const session = verifyOwnerSession((await cookies()).get("miyora_owner_session")?.value);
  if (!session) return <main className="login-screen"><a className="primary-button" href="/api/auth/discord">Entrar</a></main>;
  let economy: { implemented: boolean; guild_count: number; total_balance: number } = { implemented: false, guild_count: 0, total_balance: 0 };
  try { economy = await callBotAdmin("/economy") as typeof economy; } catch {}

  return (
    <AdminShell title="Economia Miyora" eyebrow="Sistema global" active="/economia">
      <div className="notice">{economy.implemented ? "Dados econômicos disponíveis pela API." : "A API econômica não confirmou dados neste momento. Nenhum saldo ou operação foi inventado."}</div>
      <EconomyAdmin />
    </AdminShell>
  );
}
