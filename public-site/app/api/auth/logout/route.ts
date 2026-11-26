import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const response = NextResponse.json({ ok: true });
  response.cookies.delete("miyora_session");
  response.cookies.delete("miyora_oauth_state");
  return response;
}
