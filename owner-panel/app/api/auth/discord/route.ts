import crypto from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  const clientId = process.env.OWNER_DISCORD_CLIENT_ID;
  const redirectUri = process.env.OWNER_DISCORD_REDIRECT_URI;
  if (!clientId || !redirectUri) return NextResponse.json({ error: "Owner OAuth is not configured", code: "oauth_not_configured" }, { status: 503 });

  const state = crypto.randomBytes(32).toString("base64url");
  const params = new URLSearchParams({ client_id: clientId, redirect_uri: redirectUri, response_type: "code", scope: "identify", state });
  const response = NextResponse.redirect(`https://discord.com/oauth2/authorize?${params}`);
  response.cookies.set("miyora_owner_oauth_state", state, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: 600 });
  return response;
}
