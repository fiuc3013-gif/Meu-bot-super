import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../lib/auth";
import { callBotAdmin } from "../../../../lib/bot-client";

export async function GET(request: NextRequest) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  try { return NextResponse.json(await callBotAdmin("/audit")); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
