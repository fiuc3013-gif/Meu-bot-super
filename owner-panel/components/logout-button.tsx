"use client";

export function LogoutButton() {
  async function logout() { await fetch("/api/auth/logout", { method: "POST" }); window.location.href = "/"; }
  return <button className="secondary-button" type="button" onClick={logout}>Sair</button>;
}
