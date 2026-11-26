import { NextRequest, NextResponse } from "next/server";
import { verifyOwnerRequest } from "../../../../../../lib/auth";
import { callBotAdmin } from "../../../../../../lib/bot-client";

export async function PUT(request: NextRequest, context: { params: Promise<{ productId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { productId } = await context.params;
  if (!/^\d+$/.test(productId)) return NextResponse.json({ error: "Invalid product_id", code: "validation_error" }, { status: 400 });
  const body = await request.json().catch(() => null);
  if (!body) return NextResponse.json({ error: "Invalid product", code: "validation_error" }, { status: 400 });
  try { return NextResponse.json(await callBotAdmin(`/store/products/${productId}`, { method: "PUT", body: JSON.stringify(body) })); } catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ productId: string }> }) {
  if (!verifyOwnerRequest(request)) return NextResponse.json({ error: "Forbidden", code: "forbidden" }, { status: 403 });
  const { productId } = await context.params;
  if (!/^\d+$/.test(productId)) return NextResponse.json({ error: "Invalid product_id", code: "validation_error" }, { status: 400 });
  try { return NextResponse.json(await callBotAdmin(`/store/products/${productId}`, { method: "DELETE" })); } catch { return NextResponse.json({ error: "Bot service unavailable", code: "upstream_unavailable" }, { status: 503 }); }
}
