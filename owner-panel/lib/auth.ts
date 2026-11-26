import crypto from "node:crypto";

export type OwnerSession = {
  sub: string;
  username: string;
  exp: number;
};

export function signOwnerSession(session: OwnerSession): string | null {
  const secret = process.env.OWNER_API_SESSION_SECRET;
  if (!secret) return null;
  const payload = Buffer.from(JSON.stringify(session)).toString("base64url");
  const signature = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  return `${payload}.${signature}`;
}

export function verifyOwnerRequest(request: Request) {
  const cookie = request.headers.get("cookie") ?? "";
  const match = cookie.match(/(?:^|;\s*)miyora_owner_session=([^;]+)/);
  if (match) {
    const session = verifyOwnerSession(decodeURIComponent(match[1]));
    if (session) return true;
  }

  const authorization = request.headers.get("authorization");
  const expected = process.env.OWNER_API_SESSION_SECRET;
  return Boolean(expected && authorization === `Bearer ${expected}`);
}

export function verifyOwnerSession(cookie: string | undefined): OwnerSession | null {
  if (!cookie) return null;
  const secret = process.env.OWNER_API_SESSION_SECRET;
  if (!secret) return null;
  const parts = cookie.split(".");
  if (parts.length !== 2) return null;
  const [payload, signature] = parts;
  const expected = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  const received = Buffer.from(signature);
  if (received.length !== Buffer.from(expected).length || !crypto.timingSafeEqual(Buffer.from(expected), received)) return null;
  try {
    const session = JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as OwnerSession;
    return session.sub && session.exp >= Date.now() ? session : null;
  } catch {
    return null;
  }
}
