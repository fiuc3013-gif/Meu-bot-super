export async function callBotAdmin(path: string, init: RequestInit = {}) {
  const baseUrl = process.env.BOT_API_BASE_URL;
  const token = process.env.OWNER_API_TOKEN;
  if (!baseUrl || !token) throw new Error("Administrative bot API is not configured");

  const response = await fetch(`${baseUrl.replace(/\/$/, "")}/api/v1/admin${path}`, {
    ...init,
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
    cache: "no-store",
  });
  const body = await response.json().catch(() => ({ error: "Invalid upstream response", code: "bad_upstream" }));
  if (!response.ok) throw new Error(typeof body.error === "string" ? body.error : "Administrative request failed");
  return body;
}
