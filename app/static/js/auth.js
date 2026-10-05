// Auth helpers used across pages
function getUser() {
  try { return JSON.parse(localStorage.getItem("user") || "null"); }
  catch { return null; }
}

function updateAuthUI() {
  const user = getUser();
  const token = localStorage.getItem("token");
  document.querySelectorAll("[data-auth]").forEach(el => el.hidden = !user);
  document.querySelectorAll("[data-guest]").forEach(el => el.hidden = !!user);
  document.querySelectorAll("[data-admin]").forEach(el => el.hidden = !(user && user.role === "admin"));
}

async function updateCartCount() {
  const token = localStorage.getItem("token");
  const el = document.getElementById("cart-count");
  if (!el) return;
  if (!token) { el.textContent = "0"; return; }
  try {
    const r = await fetch("/api/cart", { headers: { "Authorization": `Bearer ${token}` } });
    if (!r.ok) return;
    const { cart } = await r.json();
    el.textContent = cart.items.reduce((s, i) => s + i.quantity, 0);
  } catch {}
}

document.getElementById("logout-btn")?.addEventListener("click", (e) => {
  e.preventDefault();
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  location.href = "/";
});

updateAuthUI();
updateCartCount();
window.addEventListener("storage", () => { updateAuthUI(); updateCartCount(); });