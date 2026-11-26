import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../../../lib/auth";
import { callBotAdmin } from "../../../../../../../lib/bot-client";

export async function GET(request: NextRequest, context: { params: Promise<{ memberId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { memberId } = await context.params;
  if (!/^\d+$/.test(memberId)) return NextResponse.json({ error: "Invalid member_id", code: "validation_error" }, { status: 400 });
  try { return NextResponse.json(await callBotAdmin(`/members/${memberId}/transactions`)); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
