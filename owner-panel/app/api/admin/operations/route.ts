import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../lib/auth";
import { ownerRateLimit } from "../../../../lib/rate-limit";
import { callBotAdmin } from "../../../../lib/bot-client";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  if (!ownerRateLimit("owner:operations")) return NextResponse.json({ error: "Too many requests", code: "rate_limited" }, { status: 429 });
  const body = await request.json().catch(() => null);
  if (!body || typeof body.operation !== "string" || (body.guild_id && !/^\d+$/.test(body.guild_id))) {
    return NextResponse.json({ error: "Invalid operation", code: "validation_error" }, { status: 400 });
  }
  if (body.operation === "adjust-balance") {
    if (typeof body.amount !== "number" || !Number.isFinite(body.amount) || typeof body.reason !== "string" || body.reason.trim().length < 3 || !/^\d+$/.test(body.user_id ?? "")) {
      return NextResponse.json({ error: "Invalid balance adjustment", code: "validation_error" }, { status: 400 });
    }
  }
  if (body.operation === "adjust-balance") {
    try {
      return NextResponse.json(await callBotAdmin("/balances/adjust", { method: "POST", body: JSON.stringify({ user_id: body.user_id, guild_id: body.guild_id ?? null, amount: body.amount, reason: body.reason.trim() }) }), { status: 202 });
    } catch {
      return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 });
    }
  }
  try { return NextResponse.json(await callBotAdmin("/operations", { method: "POST", body: JSON.stringify(body) }), { status: 202 }); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
