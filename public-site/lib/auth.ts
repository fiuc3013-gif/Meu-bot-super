import crypto from "node:crypto";

export type PublicSession = {
  sub: string;
  guildIds: string[];
  exp: number;
  guilds: Array<{ id: string; name: string; icon: string | null }>;
  user: {
    id: string;
    username: string;
    avatar: string | null;
  };
};

export function signPublicSession(session: PublicSession): string | null {
  const secret = process.env.PUBLIC_API_SESSION_SECRET;
  if (!secret) return null;
  const payload = Buffer.from(JSON.stringify(session)).toString("base64url");
  const signature = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  return `${payload}.${signature}`;
}

export function verifyPublicSession(cookie: string | undefined): PublicSession | null {
  if (!cookie) return null;
  const secret = process.env.PUBLIC_API_SESSION_SECRET;
  if (!secret) return null;

  const parts = cookie.split(".");
  if (parts.length !== 2) return null;
  const [payload, signature] = parts;
  const expected = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  const received = Buffer.from(signature);
  const valid = Buffer.from(expected).length === received.length && crypto.timingSafeEqual(Buffer.from(expected), received);
  if (!valid) return null;

  try {
    const session = JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as PublicSession;
    if (!session.sub || !Array.isArray(session.guildIds) || !Array.isArray(session.guilds) || !session.user || session.exp < Date.now()) return null;
    return session;
  } catch {
    return null;
  }
}
