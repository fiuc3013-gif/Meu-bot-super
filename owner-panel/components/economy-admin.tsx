"use client";

import { useEffect, useState } from "react";

type Product = { id: number; name: string; price: string; stock: number | null };
type Loan = { id: number; user_id: string; requested_amount: string; approved_amount: string | null; installments: number; status: string };
type Booster = { id: number; user_id: string; benefit: string; status: string };

export function EconomyAdmin() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [boosters, setBoosters] = useState<Booster[]>([]);
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    const [p, l, b] = await Promise.all([
      fetch("/api/admin/store/products", { cache: "no-store" }).then((r) => r.json()).catch(() => ({ products: [] })),
      fetch("/api/admin/loans", { cache: "no-store" }).then((r) => r.json()).catch(() => ({ loans: [] })),
      fetch("/api/admin/boosters?status=pending", { cache: "no-store" }).then((r) => r.json()).catch(() => ({ requests: [] })),
    ]);
    setProducts(p.products || []); setLoans(l.loans || []); setBoosters(b.requests || []);
  }

  useEffect(() => { load(); }, []);

  async function createProduct() {
    setMessage("");
    const stockValue = stock === "" ? null : Number(stock);
    const response = await fetch("/api/admin/store/products", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, description: "", price: Number(price), stock: stockValue, guild_id: null }) });
    const body = await response.json();
    if (!response.ok) { setMessage(body.error || "Não foi possível criar o produto."); return; }
    setName(""); setPrice(""); setStock(""); setMessage("Produto criado."); await load();
  }

  async function editProduct(product: Product) {
    const nextName = window.prompt("Nome do produto", product.name) ?? "";
    const nextPrice = window.prompt("Preço", product.price) ?? "";
    const nextStock = window.prompt("Estoque (vazio = ilimitado)", product.stock?.toString() ?? "") ?? "";
    if (!nextName.trim() || !Number.isFinite(Number(nextPrice)) || Number(nextPrice) <= 0) { setMessage("Dados do produto inválidos."); return; }
    const stockValue = nextStock === "" ? null : Number(nextStock);
    if (stockValue !== null && (!Number.isInteger(stockValue) || stockValue < 0)) { setMessage("Estoque inválido."); return; }
    const response = await fetch(`/api/admin/store/products/${product.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name: nextName.trim(), description: "", price: Number(nextPrice), stock: stockValue, guild_id: null }) });
    setMessage(response.ok ? "Produto atualizado." : "Não foi possível atualizar o produto."); await load();
  }

  async function removeProduct(id: number) {
    if (!window.confirm("Remover este produto do catálogo ativo?")) return;
    const response = await fetch(`/api/admin/store/products/${id}`, { method: "DELETE" });
    if (!response.ok) { setMessage("Não foi possível remover o produto."); return; }
    setMessage("Produto removido."); await load();
  }

  async function decideLoan(id: number, approve: boolean) {
    if (!window.confirm(approve ? "Aprovar este empréstimo?" : "Recusar este empréstimo?")) return;
    const reason = window.prompt("Motivo da decisão:", approve ? "Aprovado pelo proprietário" : "Recusado após análise") || "";
    if (!reason.trim()) return;
    const approvedAmount: number | null = approve ? Number(window.prompt("Valor aprovado:", "") || 0) : null;
    if (approve && (approvedAmount === null || !Number.isFinite(approvedAmount) || approvedAmount <= 0 || approvedAmount > 50000)) { setMessage("Valor aprovado inválido."); return; }
    const response = await fetch(approve ? `/api/admin/loans/${id}/approve` : `/api/admin/loans/${id}/reject`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ approved_amount: approvedAmount, reason }) });
    setMessage(response.ok ? "Decisão registrada." : "Não foi possível registrar a decisão."); await load();
  }

  async function showLoanPayments(id: number) {
    const response = await fetch(`/api/admin/loans/${id}/payments`, { cache: "no-store" });
    const body = await response.json();
    if (!response.ok) { setMessage(body.error || "Não foi possível consultar parcelas."); return; }
    const rows = (body.payments || []).map((payment: { installment: number; amount: string; due_at: string; paid_at: string | null }) => `${payment.installment}: ${payment.amount} - ${payment.paid_at ? "paga" : `vence ${payment.due_at}`}`).join("\n");
    window.alert(rows || "Nenhuma parcela encontrada.");
  }

  async function payLoanInstallment(id: number) {
    const value = window.prompt("Número da parcela a pagar:", "1") ?? "";
    if (!/^\d+$/.test(value) || Number(value) < 1) { setMessage("Parcela inválida."); return; }
    if (!window.confirm(`Registrar pagamento da parcela ${value}?`)) return;
    const response = await fetch(`/api/admin/loans/${id}/payments/${value}`, { method: "POST" });
    setMessage(response.ok ? "Pagamento registrado." : "Não foi possível registrar o pagamento."); await load();
  }

  async function decideBooster(id: number, approve: boolean) {
    if (!window.confirm(approve ? "Aprovar benefício do booster?" : "Recusar benefício do booster?")) return;
    const reason = window.prompt("Motivo da decisão:", "") || "";
    if (!reason.trim()) return;
    const response = await fetch(`/api/admin/boosters/${id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ approve, reason }) });
    setMessage(response.ok ? "Decisão registrada." : "Não foi possível registrar a decisão."); await load();
  }

  return (
    <>
      {message && <p className="notice" role="status">{message}</p>}
      <section className="table-panel"><h2>Loja global</h2><div className="search-row"><input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nome do produto" /><input value={price} onChange={(e) => setPrice(e.target.value)} placeholder="Preço" type="number" min="0.01" /><input value={stock} onChange={(e) => setStock(e.target.value)} placeholder="Estoque (vazio = ilimitado)" type="number" min="0" /><button className="primary-button" type="button" onClick={createProduct}>Criar</button></div><table><thead><tr><th>Produto</th><th>Preço</th><th>Estoque</th><th>Ação</th></tr></thead><tbody>{products.map((product) => <tr key={product.id}><td>{product.name}</td><td>{product.price}</td><td>{product.stock ?? "Ilimitado"}</td><td><button className="secondary-button" type="button" onClick={() => editProduct(product)}>Editar</button> <button className="secondary-button" type="button" onClick={() => removeProduct(product.id)}>Remover</button></td></tr>)}</tbody></table></section>
      <section className="table-panel"><h2>Empréstimos</h2><table><thead><tr><th>ID</th><th>Usuário</th><th>Solicitado</th><th>Parcelas</th><th>Status</th><th>Ações</th></tr></thead><tbody>{loans.map((loan) => <tr key={loan.id}><td>{loan.id}</td><td>{loan.user_id}</td><td>{loan.requested_amount}</td><td>{loan.installments}</td><td>{loan.status}</td><td><button className="primary-button" type="button" onClick={() => decideLoan(loan.id, true)}>Aprovar</button> <button className="secondary-button" type="button" onClick={() => decideLoan(loan.id, false)}>Recusar</button> <button className="secondary-button" type="button" onClick={() => showLoanPayments(loan.id)}>Parcelas</button> <button className="secondary-button" type="button" onClick={() => payLoanInstallment(loan.id)}>Pagar</button></td></tr>)}</tbody></table></section>
      <section className="table-panel"><h2>Boosters pendentes</h2><table><thead><tr><th>ID</th><th>Usuário</th><th>Benefício</th><th>Ações</th></tr></thead><tbody>{boosters.map((item) => <tr key={item.id}><td>{item.id}</td><td>{item.user_id}</td><td>{item.benefit}</td><td><button className="primary-button" type="button" onClick={() => decideBooster(item.id, true)}>Aprovar</button> <button className="secondary-button" type="button" onClick={() => decideBooster(item.id, false)}>Recusar</button></td></tr>)}</tbody></table></section>
    </>
  );
}
