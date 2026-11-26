import { NextRequest, NextResponse } from "next/server";
import { verifyPublicSession } from "../../../../../../lib/auth";
import { callBot } from "../../../../../../lib/bot-client";

export const dynamic = "force-dynamic";

function authorize(request: NextRequest, guildId: string) {
  const session = verifyPublicSession(request.cookies.get("miyora_session")?.value);
  if (!session) return NextResponse.json({ error: "Unauthorized", code: "unauthorized" }, { status: 401 });
  if (!/^\d+$/.test(guildId) || !session.guildIds.includes(guildId)) return NextResponse.json({ error: "Forbidden", code: "guild_access_denied" }, { status: 403 });
  return null;
}

export async function GET(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  const { guildId } = await context.params;
  const denied = authorize(request, guildId);
  if (denied) return denied;
  try { return NextResponse.json(await callBot(`/api/v1/guilds/${guildId}/store/products`)); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}

export async function POST(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  const { guildId } = await context.params;
  const denied = authorize(request, guildId);
  if (denied) return denied;
  const body = await request.json().catch(() => null);
  if (!body || !Number.isInteger(body.product_id) || body.product_id <= 0 || typeof body.idempotency_key !== "string" || body.idempotency_key.length < 3) {
    return NextResponse.json({ error: "Invalid purchase", code: "validation_error" }, { status: 400 });
  }
  const session = verifyPublicSession(request.cookies.get("miyora_session")?.value);
  try {
    return NextResponse.json(await callBot(`/api/v1/guilds/${guildId}/store/purchase`, {
      method: "POST",
      body: JSON.stringify({ product_id: body.product_id, user_id: session?.sub, idempotency_key: body.idempotency_key }),
    }), { status: 201 });
  } catch {
    return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 });
  }
}
