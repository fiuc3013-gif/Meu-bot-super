import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../../lib/auth";
import { callBotAdmin } from "../../../../../../lib/bot-client";

export async function POST(request: NextRequest, context: { params: Promise<{ loanId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { loanId } = await context.params;
  const body = await request.json().catch(() => null);
  if (!/^\d+$/.test(loanId) || !body || typeof body.reason !== "string") return NextResponse.json({ error: "Invalid approval", code: "validation_error" }, { status: 400 });
  try { return NextResponse.json(await callBotAdmin(`/loans/${loanId}/approve`, { method: "POST", body: JSON.stringify(body) }), { status: 202 }); } catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
