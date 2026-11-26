"use client";

import { useEffect, useState } from "react";

export function GuildConfigPanel({ guildId }: { guildId: string }) {
  const [locale, setLocale] = useState("pt-BR");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [welcomeChannel, setWelcomeChannel] = useState("");
  const [welcomeTemplate, setWelcomeTemplate] = useState("Bem-vindo, {member}, ao {guild}!\n");
  const [leaveTemplate, setLeaveTemplate] = useState("{member} saiu de {guild}.\n");
  const [channels, setChannels] = useState<Array<{ id: string; name: string }>>([]);
  const [floodEnabled, setFloodEnabled] = useState(true);
  const [floodAction, setFloodAction] = useState("record_only");

  useEffect(() => {
    let active = true;
    fetch(`/api/public/guilds/${guildId}/config`, { cache: "no-store" })
      .then(async (response) => {
        const body = await response.json();
        if (!response.ok) throw new Error(body.error || "Não foi possível carregar as configurações.");
        if (active) {
          setLocale(body.locale || "pt-BR");
          setWelcomeTemplate(body.welcome_config?.template || "Bem-vindo, {member}, ao {guild}!\n");
          setWelcomeChannel(body.welcome_config?.channel_id || "");
          setFloodEnabled(body.moderation_config?.flood?.enabled !== false);
          setFloodAction(body.moderation_config?.flood?.action || "record_only");
        }
      })
      .catch((error: Error) => { if (active) setMessage(error.message); })
      .finally(() => { if (active) setLoading(false); });
    fetch(`/api/public/guilds/${guildId}/messages`, { cache: "no-store" })
      .then(async (response) => {
        const body = await response.json();
        if (response.ok && active) {
          const welcome = (body.messages || []).find((item: { event: string }) => item.event === "welcome");
          const leave = (body.messages || []).find((item: { event: string }) => item.event === "leave");
          if (welcome) { setWelcomeTemplate(welcome.template || ""); setWelcomeChannel(welcome.channel_id || ""); }
          if (leave) setLeaveTemplate(leave.template || "");
        }
      })
      .catch(() => {});
    fetch(`/api/public/guilds/${guildId}/channels`, { cache: "no-store" })
      .then(async (response) => { const body = await response.json(); if (response.ok && active) setChannels(body.channels || []); })
      .catch(() => {});
    return () => { active = false; };
  }, [guildId]);

  async function save() {
    setSaving(true);
    setMessage("");
    try {
      const response = await fetch(`/api/public/guilds/${guildId}/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ locale, enabled_modules: ["xp", "economy", "moderação"].filter(Boolean), welcome_config: { channel_id: welcomeChannel, template: welcomeTemplate }, moderation_config: { flood: { enabled: floodEnabled, action: floodAction } } }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.error || "Não foi possível salvar.");
      if (welcomeChannel) {
        await fetch(`/api/public/guilds/${guildId}/messages`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ event: "welcome", channel_id: welcomeChannel, template: welcomeTemplate }) });
        await fetch(`/api/public/guilds/${guildId}/messages`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ event: "leave", channel_id: welcomeChannel, template: leaveTemplate }) });
      }
      await fetch(`/api/public/guilds/${guildId}/moderation/rules`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ rule_type: "flood", enabled: floodEnabled, action: floodAction }) });
      setLocale(body.locale || locale);
      setMessage("Configuração salva com sucesso.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Não foi possível salvar.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="settings-panel">
      <h2>Geral</h2>
      {loading ? <p>Carregando configurações...</p> : (
        <>
          <div className="field"><label htmlFor="locale">Idioma</label><select id="locale" value={locale} onChange={(event) => setLocale(event.target.value)}><option value="pt-BR">Português (Brasil)</option><option value="en-US">English (US)</option></select></div>
          <div className="field"><label htmlFor="welcome-channel">Canal de boas-vindas e despedidas</label><select id="welcome-channel" value={welcomeChannel} onChange={(event) => setWelcomeChannel(event.target.value)}><option value="">Não configurado</option>{channels.map((channel) => <option value={channel.id} key={channel.id}>{channel.name}</option>)}</select></div>
          <div className="field"><label htmlFor="welcome-template">Mensagem de boas-vindas</label><input id="welcome-template" value={welcomeTemplate} onChange={(event) => setWelcomeTemplate(event.target.value)} /></div>
          <div className="field"><label htmlFor="leave-template">Mensagem de despedida</label><input id="leave-template" value={leaveTemplate} onChange={(event) => setLeaveTemplate(event.target.value)} /></div>
          <div className="field"><label><input type="checkbox" checked={floodEnabled} onChange={(event) => setFloodEnabled(event.target.checked)} /> Proteção contra flood ativada</label></div>
          <div className="field"><label htmlFor="flood-action">Ação ao detectar flood</label><select id="flood-action" value={floodAction} onChange={(event) => setFloodAction(event.target.value)}><option value="record_only">Registrar somente</option><option value="timeout">Silenciar temporariamente</option></select></div>
          <div className="notice">As demais categorias ficam visíveis somente para planejamento e ainda não salvam configurações.</div>
          <button className="primary-button" type="button" onClick={save} disabled={saving}>{saving ? "Salvando..." : "Salvar configurações"}</button>
        </>
      )}
      {message && <p className="notice" role="status">{message}</p>}
    </section>
  );
}
