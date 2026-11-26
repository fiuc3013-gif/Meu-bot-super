import crypto from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { signPublicSession } from "../../../../../lib/auth";

export const dynamic = "force-dynamic";

const MANAGE_GUILD = BigInt("32");
const ADMINISTRATOR = BigInt("8");

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const savedState = request.cookies.get("miyora_oauth_state")?.value;

  const stateValid = Boolean(state && savedState && state.length === savedState.length && crypto.timingSafeEqual(Buffer.from(state), Buffer.from(savedState)));
  if (!code || !stateValid) {
    return NextResponse.redirect(new URL("/?auth=invalid", request.url));
  }

  const clientId = process.env.DISCORD_CLIENT_ID;
  const clientSecret = process.env.DISCORD_CLIENT_SECRET;
  const redirectUri = process.env.DISCORD_REDIRECT_URI;
  if (!clientId || !clientSecret || !redirectUri) {
    return NextResponse.redirect(new URL("/?auth=configuration", request.url));
  }

  const tokenResponse = await fetch("https://discord.com/api/oauth2/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      grant_type: "authorization_code",
      code,
      redirect_uri: redirectUri,
    }),
  });
  const token = await tokenResponse.json().catch(() => null) as { access_token?: string; token_type?: string } | null;
  if (!tokenResponse.ok || !token?.access_token) {
    return NextResponse.redirect(new URL("/?auth=discord", request.url));
  }

  const headers = { Authorization: `${token.token_type ?? "Bearer"} ${token.access_token}` };
  const [userResponse, guildsResponse] = await Promise.all([
    fetch("https://discord.com/api/users/@me", { headers, cache: "no-store" }),
    fetch("https://discord.com/api/users/@me/guilds", { headers, cache: "no-store" }),
  ]);
  const user = await userResponse.json().catch(() => null) as { id?: string; username?: string; avatar?: string | null } | null;
  const guilds = await guildsResponse.json().catch(() => null) as Array<{ id: string; name: string; icon: string | null; permissions: string; owner: boolean }> | null;
  if (!userResponse.ok || !guildsResponse.ok || !user?.id || !guilds) {
    return NextResponse.redirect(new URL("/?auth=discord", request.url));
  }

  const manageable = guilds.filter((guild) => {
    if (guild.owner) return true;
    const permissions = BigInt(guild.permissions || "0");
    return (permissions & ADMINISTRATOR) !== BigInt(0) || (permissions & MANAGE_GUILD) !== BigInt(0);
  });

  const exp = Date.now() + 12 * 60 * 60 * 1000;
  const cookie = signPublicSession({
    sub: user.id,
    guildIds: manageable.map((guild) => guild.id),
    guilds: manageable.map((guild) => ({ id: guild.id, name: guild.name, icon: guild.icon })),
    exp,
    user: { id: user.id, username: user.username ?? "Usuário", avatar: user.avatar ?? null },
  });
  if (!cookie) return NextResponse.redirect(new URL("/?auth=configuration", request.url));

  const response = NextResponse.redirect(new URL("/dashboard", request.url));
  response.cookies.set("miyora_session", cookie, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    expires: new Date(exp),
  });
  response.cookies.delete("miyora_oauth_state");
  return response;
}
