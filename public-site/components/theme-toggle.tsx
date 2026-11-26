"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    setTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");
  }, []);

  function toggle() {
    const next = theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("miyora-theme", next);
    setTheme(next);
  }

  return <button className="secondary-button" type="button" onClick={toggle} aria-label="Alternar tema">{theme === "dark" ? "Claro" : "Escuro"}</button>;
}
