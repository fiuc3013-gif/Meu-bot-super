import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../lib/auth";
import { ownerRateLimit } from "../../../../../lib/rate-limit";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { guildId } = await context.params;
  if (!/^\d+$/.test(guildId)) return NextResponse.json({ error: "Invalid guild_id", code: "validation_error" }, { status: 400 });
  if (!ownerRateLimit(`owner:members:${guildId}`)) return NextResponse.json({ error: "Too many requests", code: "rate_limited" }, { status: 429 });
  return NextResponse.json({ guild_id: guildId, members: [], implemented: false });
}
