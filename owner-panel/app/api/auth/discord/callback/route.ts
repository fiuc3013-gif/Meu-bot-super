import crypto from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { signOwnerSession } from "../../../../../lib/auth";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state") ?? "";
  const savedState = request.cookies.get("miyora_owner_oauth_state")?.value ?? "";
  const stateValid = state.length === savedState.length && crypto.timingSafeEqual(Buffer.from(state), Buffer.from(savedState));
  if (!code || !stateValid) return NextResponse.redirect(new URL("/?auth=invalid", request.url));

  const clientId = process.env.OWNER_DISCORD_CLIENT_ID;
  const clientSecret = process.env.OWNER_DISCORD_CLIENT_SECRET;
  const redirectUri = process.env.OWNER_DISCORD_REDIRECT_URI;
  const ownerId = process.env.OWNER_DISCORD_USER_ID;
  if (!clientId || !clientSecret || !redirectUri || !ownerId) return NextResponse.redirect(new URL("/?auth=configuration", request.url));

  const tokenResponse = await fetch("https://discord.com/api/oauth2/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ client_id: clientId, client_secret: clientSecret, grant_type: "authorization_code", code, redirect_uri: redirectUri }),
  });
  const token = await tokenResponse.json().catch(() => null) as { access_token?: string; token_type?: string } | null;
  if (!tokenResponse.ok || !token?.access_token) return NextResponse.redirect(new URL("/?auth=discord", request.url));

  const userResponse = await fetch("https://discord.com/api/users/@me", { headers: { Authorization: `${token.token_type ?? "Bearer"} ${token.access_token}` }, cache: "no-store" });
  const user = await userResponse.json().catch(() => null) as { id?: string; username?: string } | null;
  if (!userResponse.ok || !user?.id || user.id !== ownerId) return NextResponse.redirect(new URL("/?auth=denied", request.url));

  const exp = Date.now() + 8 * 60 * 60 * 1000;
  const cookie = signOwnerSession({ sub: user.id, username: user.username ?? "Proprietário", exp });
  if (!cookie) return NextResponse.redirect(new URL("/?auth=configuration", request.url));

  const response = NextResponse.redirect(new URL("/dashboard", request.url));
  response.cookies.set("miyora_owner_session", cookie, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", expires: new Date(exp) });
  response.cookies.delete("miyora_owner_oauth_state");
  return response;
}
