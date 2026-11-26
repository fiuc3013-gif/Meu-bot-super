import { NextRequest, NextResponse } from "next/server";
import { verifyPublicSession } from "../../../../lib/auth";
import { callBot } from "../../../../lib/bot-client";
import { publicRateLimit } from "../../../../lib/rate-limit";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const session = verifyPublicSession(request.cookies.get("miyora_session")?.value);
  if (!session) return NextResponse.json({ error: "Unauthorized", code: "unauthorized" }, { status: 401 });
  if (!publicRateLimit(session.sub)) return NextResponse.json({ error: "Too many requests", code: "rate_limited" }, { status: 429 });
  try {
    const all = await callBot("/api/v1/guilds") as { guilds: Array<{ guild_id: string; name: string }> };
    const allowed = all.guilds.filter((guild) => session.guildIds.includes(guild.guild_id));
    return NextResponse.json({ guilds: allowed });
  } catch {
    return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 });
  }
}
