import { NextRequest, NextResponse } from "next/server";
import { verifyPublicSession } from "../../../../../../lib/auth";
import { callBot } from "../../../../../../lib/bot-client";

export async function GET(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  const session = verifyPublicSession(request.cookies.get("miyora_session")?.value);
  const { guildId } = await context.params;
  if (!session) return NextResponse.json({ error: "Unauthorized", code: "unauthorized" }, { status: 401 });
  if (!/^\d+$/.test(guildId) || !session.guildIds.includes(guildId)) return NextResponse.json({ error: "Forbidden", code: "guild_access_denied" }, { status: 403 });
  try { return NextResponse.json(await callBot(`/api/v1/guilds/${guildId}/roles`)); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
