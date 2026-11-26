import Link from "next/link";
import type { ReactNode } from "react";
import { ThemeToggle } from "./theme-toggle";
import { LogoutButton } from "./logout-button";

const items = [
  ["/dashboard", "Dashboard"], ["/servidores", "Servidores"], ["/membros", "Membros"],
  ["/economia", "Economia"], ["/logs", "Logs e auditoria"],
];

export function AdminShell({ title, eyebrow, children, active = "/dashboard" }: { title: string; eyebrow: string; children: ReactNode; active?: string }) {
  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <Link className="sidebar-brand" href="/dashboard"><span className="brand-mark">M</span><span>Miyora Admin</span></Link>
        <nav className="side-nav" aria-label="Navegação administrativa">{items.map(([href, label]) => <Link className={active === href ? "active" : ""} href={href} key={href}><span>{label}</span></Link>)}</nav>
        <div className="sidebar-footer"><ThemeToggle /><LogoutButton /></div>
      </aside>
      <main className="admin-main">
        <header className="admin-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1></div></header>
        {children}
      </main>
    </div>
  );
}
