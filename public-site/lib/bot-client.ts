export async function callBot(path: string, init: RequestInit = {}) {
  const baseUrl = process.env.BOT_API_BASE_URL;
  const token = process.env.BOT_API_TOKEN;
  if (!baseUrl || !token) {
    throw new Error("Bot API is not configured");
  }

  const response = await fetch(`${baseUrl.replace(/\/$/, "")}${path}`, {
    ...init,
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      ...init.headers,
    },
    cache: "no-store",
  });

  const body = await response.json().catch(() => ({ error: "Invalid upstream response", code: "bad_upstream" }));
  if (!response.ok) {
    throw new Error(typeof body.error === "string" ? body.error : "Bot API request failed");
  }
  return body;
}
