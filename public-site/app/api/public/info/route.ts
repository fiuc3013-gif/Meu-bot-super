import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export function GET() {
  return NextResponse.json({ name: "Miyora", status: "ready", future_modules: [] });
}
