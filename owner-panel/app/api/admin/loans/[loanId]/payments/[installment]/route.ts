import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../../../lib/auth";
import { callBotAdmin } from "../../../../../../../lib/bot-client";

export async function POST(request: NextRequest, context: { params: Promise<{ loanId: string; installment: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { loanId, installment } = await context.params;
  if (!/^\d+$/.test(loanId) || !/^\d+$/.test(installment)) return NextResponse.json({ error: "Invalid payment", code: "validation_error" }, { status: 400 });
  try { return NextResponse.json(await callBotAdmin(`/loans/${loanId}/payments/${installment}`, { method: "POST" }), { status: 202 }); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
