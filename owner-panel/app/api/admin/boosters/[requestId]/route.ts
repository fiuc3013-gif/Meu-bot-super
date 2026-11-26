import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../lib/auth";
import { callBotAdmin } from "../../../../../lib/bot-client";

export async function POST(request: NextRequest, context: { params: Promise<{ requestId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { requestId } = await context.params;
  const body = await request.json().catch(() => null);
  if (!/^\d+$/.test(requestId) || !body || typeof body.approve !== "boolean" || typeof body.reason !== "string") return NextResponse.json({ error: "Invalid booster decision", code: "validation_error" }, { status: 400 });
  try { return NextResponse.json(await callBotAdmin(`/boosters/${requestId}/decision`, { method: "POST", body: JSON.stringify(body) }), { status: 202 }); } catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
