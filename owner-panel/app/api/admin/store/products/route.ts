import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../lib/auth";
import { callBotAdmin } from "../../../../../lib/bot-client";

export async function GET(request: NextRequest) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  try { return NextResponse.json(await callBotAdmin("/store/products")); } catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}

export async function POST(request: NextRequest) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const body = await request.json().catch(() => null);
  if (!body || typeof body.name !== "string" || !Number.isFinite(body.price) || body.price <= 0 || (body.stock !== null && (!Number.isInteger(body.stock) || body.stock < 0))) {
    return NextResponse.json({ error: "Invalid product", code: "validation_error" }, { status: 400 });
  }
  try { return NextResponse.json(await callBotAdmin("/store/products", { method: "POST", body: JSON.stringify(body) }), { status: 201 }); } catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
