import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../lib/auth";
import { ownerRateLimit } from "../../../../lib/rate-limit";
import { callBotAdmin } from "../../../../lib/bot-client";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  if (!ownerRateLimit("owner:stats")) return NextResponse.json({ error: "Too many requests", code: "rate_limited" }, { status: 429 });
  try { return NextResponse.json(await callBotAdmin("/stats")); }
  catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
