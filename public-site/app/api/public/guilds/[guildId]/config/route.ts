import { NextRequest, NextResponse } from "next/server";
import { verifyPublicSession } from "../../../../../../lib/auth";
import { callBot } from "../../../../../../lib/bot-client";
import { publicRateLimit } from "../../../../../../lib/rate-limit";

export const dynamic = "force-dynamic";

function authorize(request: NextRequest, guildId: string) {
  const session = verifyPublicSession(request.cookies.get("miyora_session")?.value);
  if (!session) return { session: null, response: NextResponse.json({ error: "Unauthorized", code: "unauthorized" }, { status: 401 }) };
  if (!session.guildIds.includes(guildId)) return { session: null, response: NextResponse.json({ error: "Forbidden", code: "guild_access_denied" }, { status: 403 }) };
  if (!publicRateLimit(`${session.sub}:${guildId}`)) return { session: null, response: NextResponse.json({ error: "Too many requests", code: "rate_limited" }, { status: 429 }) };
  return { session, response: null };
}

export async function GET(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  const { guildId } = await context.params;
  if (!/^\d+$/.test(guildId)) return NextResponse.json({ error: "Invalid guild_id", code: "validation_error" }, { status: 400 });
  const { response } = authorize(request, guildId);
  if (response) return response;
  try {
    return NextResponse.json(await callBot(`/api/v1/guilds/${guildId}/config`));
  } catch {
    return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 });
  }
}

export async function PUT(request: NextRequest, context: { params: Promise<{ guildId: string }> }) {
  const { guildId } = await context.params;
  if (!/^\d+$/.test(guildId)) return NextResponse.json({ error: "Invalid guild_id", code: "validation_error" }, { status: 400 });
  const { response } = authorize(request, guildId);
  if (response) return response;

  const body = await request.json().catch(() => null);
  const locale = typeof body?.locale === "string" ? body.locale : null;
  const enabledModules = Array.isArray(body?.enabled_modules) ? body.enabled_modules : [];
  const welcomeConfig = body?.welcome_config && typeof body.welcome_config === "object" ? body.welcome_config : {};
  const moderationConfig = body?.moderation_config && typeof body.moderation_config === "object" ? body.moderation_config : {};
  const xpConfig = body?.xp_config && typeof body.xp_config === "object" ? body.xp_config : {};
  const economyConfig = body?.economy_config && typeof body.economy_config === "object" ? body.economy_config : {};
  const ticketConfig = body?.ticket_config && typeof body.ticket_config === "object" ? body.ticket_config : {};
  if (!locale || !/^([a-z]{2}-[A-Z]{2}|[a-z]{2})$/.test(locale) || enabledModules.length > 50) {
    return NextResponse.json({ error: "Invalid configuration", code: "validation_error" }, { status: 400 });
  }

  try {
    return NextResponse.json(await callBot(`/api/v1/guilds/${guildId}/config`, {
      method: "PUT",
      body: JSON.stringify({ locale, enabled_modules: enabledModules, welcome_config: welcomeConfig, moderation_config: moderationConfig, xp_config: xpConfig, economy_config: economyConfig, ticket_config: ticketConfig }),
    }));
  } catch {
    return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 });
  }
}
