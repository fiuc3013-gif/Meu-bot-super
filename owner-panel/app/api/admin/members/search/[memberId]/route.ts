import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../../lib/auth";
import { ownerRateLimit } from "../../../../../../lib/rate-limit";
import { callBotAdmin } from "../../../../../../lib/bot-client";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest, context: { params: Promise<{ memberId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { memberId } = await context.params;
  if (!/^\d+$/.test(memberId)) return NextResponse.json({ error: "Invalid member_id", code: "validation_error" }, { status: 400 });
  if (!ownerRateLimit(`owner:member:${memberId}`)) return NextResponse.json({ error: "Too many requests", code: "rate_limited" }, { status: 429 });
  try { return NextResponse.json(await callBotAdmin(`/members/${memberId}`)); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
