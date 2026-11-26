import { NextRequest, NextResponse } from "next/server";
import { verifyPublicSession } from "../../../../../../../lib/auth";
import { callBot } from "../../../../../../../lib/bot-client";

export async function PUT(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  const session = verifyPublicSession(request.cookies.get("miyora_session")?.value);
  const { guildId } = await context.params;
  if (!session) return NextResponse.json({ error: "Unauthorized", code: "unauthorized" }, { status: 401 });
  if (!/^\d+$/.test(guildId) || !session.guildIds.includes(guildId)) return NextResponse.json({ error: "Forbidden", code: "guild_access_denied" }, { status: 403 });
  const body = await request.json().catch(() => null);
  const validList = (value: unknown) => value === undefined || (Array.isArray(value) && value.every((item) => typeof item === "string"));
  if (!body || !["flood", "invite_filter", "trap"].includes(body.rule_type) || typeof body.enabled !== "boolean" || !["record_only", "timeout", "kick", "ban"].includes(body.action) || (body.channel_id !== undefined && body.channel_id !== null && !/^\d+$/.test(body.channel_id)) || !validList(body.keywords) || !validList(body.except_users) || !validList(body.except_roles)) {
    return NextResponse.json({ error: "Invalid moderation rule", code: "validation_error" }, { status: 400 });
  }
  try { return NextResponse.json(await callBot(`/api/v1/guilds/${guildId}/moderation/rules`, { method: "PUT", body: JSON.stringify({ rule_type: body.rule_type, enabled: body.enabled, action: body.action, channel_id: body.channel_id ?? null, keywords: body.keywords ?? [], except_users: body.except_users ?? [], except_roles: body.except_roles ?? [] }) })); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
