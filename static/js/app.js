/* Crypto Bot by ASM Traders - Frontend */

let chart = null;
let candleSeries = null;
let currentSignal = null;
let authToken = localStorage.getItem("cb_token") || null;
let currentUser = JSON.parse(localStorage.getItem("cb_user") || "null");

// ---------- Auth Helpers ----------
function setAuth(token, user) {
  authToken = token;
  currentUser = user;
  localStorage.setItem("cb_token", token);
  localStorage.setItem("cb_user", JSON.stringify(user));
  updateHeader();
  loadDemoAccount();
  loadBlogPosts();
}

function clearAuth() {
  authToken = null;
  currentUser = null;
  localStorage.removeItem("cb_token");
  localStorage.removeItem("cb_user");
  updateHeader();
  document.getElementById("demoAccount").innerHTML = `<p class="muted">Login to start paper trading with virtual balance.</p>`;
  document.getElementById("tradeHistory").innerHTML = `<p class="muted">No trades yet.</p>`;
  document.getElementById("accountTitle").textContent = "Login to unlock full features";
  document.getElementById("accountDesc").textContent = "Register for free to access demo trading, save signals and manage your paper portfolio.";
  document.getElementById("accountActions").innerHTML = `<button class="btn primary" onclick="openModal('register')">Create Free Account</button>`;
}

function authHeaders() {
  return authToken ? { Authorization: `Bearer ${authToken}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
}

function updateHeader() {
  const el = document.getElementById("headerActions");
  if (currentUser) {
    el.innerHTML = `
      <span style="color:var(--muted);font-size:13px;margin-right:8px;">Hi, ${currentUser.username}</span>
      <button class="btn ghost" onclick="clearAuth()">Logout</button>
    `;
    document.getElementById("accountTitle").textContent = `Welcome, ${currentUser.full_name || currentUser.username}`;
    document.getElementById("accountDesc").textContent = `Plan: ${(currentUser.plan || "free").toUpperCase()} · Demo trading & signals unlocked.`;
    document.getElementById("accountActions").innerHTML = `<button class="btn ghost" onclick="clearAuth()">Logout</button>`;
  } else {
    el.innerHTML = `
      <button class="btn ghost" onclick="openModal('login')">Login</button>
      <button class="btn primary" onclick="openModal('register')">Get Started</button>
    `;
  }
}

// ---------- Modal ----------
function openModal(type) {
  document.getElementById("authModal").classList.add("active");
  switchAuth(type);
  document.getElementById("authError").textContent = "";
}
function closeModal() {
  document.getElementById("authModal").classList.remove("active");
}
function switchAuth(type) {
  document.getElementById("loginForm").style.display = type === "login" ? "block" : "none";
  document.getElementById("registerForm").style.display = type === "register" ? "block" : "none";
  document.getElementById("authError").textContent = "";
}

async function doLogin() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const err = document.getElementById("authError");
  err.textContent = "";
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");
    setAuth(data.access_token, data.user);
    closeModal();
  } catch (e) {
    err.textContent = e.message;
  }
}

async function doRegister() {
  const username = document.getElementById("regUsername").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const full_name = document.getElementById("regFullName").value.trim();
  const err = document.getElementById("authError");
  err.textContent = "";
  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password, full_name }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed");
    setAuth(data.access_token, data.user);
    closeModal();
  } catch (e) {
    err.textContent = e.message;
  }
}

// ---------- Chart (Lightweight Charts) ----------
function initChart() {
  const container = document.getElementById("chart");
  if (!container) return;
  chart = LightweightCharts.createChart(container, {
    layout: {
      background: { type: "solid", color: "transparent" },
      textColor: "#91a6c0",
    },
    grid: {
      vertLines: { color: "rgba(148,163,184,0.08)" },
      horzLines: { color: "rgba(148,163,184,0.08)" },
    },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
    rightPriceScale: { borderColor: "rgba(148,163,184,0.2)" },
    timeScale: { borderColor: "rgba(148,163,184,0.2)", timeVisible: true },
    width: container.clientWidth,
    height: 420,
  });
  candleSeries = chart.addCandlestickSeries({
    upColor: "#4ade80",
    downColor: "#fb7185",
    borderUpColor: "#4ade80",
    borderDownColor: "#fb7185",
    wickUpColor: "#4ade80",
    wickDownColor: "#fb7185",
  });
  window.addEventListener("resize", () => {
    if (chart && container) {
      chart.applyOptions({ width: container.clientWidth });
    }
  });
}

// ---------- Dashboard ----------
async function loadDashboard() {
  const symbol = document.getElementById("symbol").value.trim().toUpperCase() || "BTCUSDT";
  const interval = document.getElementById("interval").value;
  const wantExplain = document.getElementById("aiExplain").checked;

  const signalPanel = document.getElementById("signalPanel");
  signalPanel.innerHTML = "<p class='muted'>Loading...</p>";

  try {
    const [kRes, sRes] = await Promise.all([
      fetch(`/api/market/klines?symbol=${encodeURIComponent(symbol)}&interval=${interval}&limit=200`),
      fetch(`/api/signals/current?symbol=${encodeURIComponent(symbol)}&interval=${interval}&explain=${wantExplain}`, {
        headers: authHeaders(),
      }),
    ]);

    if (!kRes.ok || !sRes.ok) {
      signalPanel.innerHTML = "<p>Market data temporarily unavailable.</p>";
      return;
    }

    const candles = await kRes.json();
    const signal = await sRes.json();
    currentSignal = signal;

    // Chart data
    const chartData = candles.map((c) => ({
      time: Math.floor(Number(c.open_time) / 1000),
      open: Number(c.open),
      high: Number(c.high),
      low: Number(c.low),
      close: Number(c.close),
    }));
    if (candleSeries) {
      candleSeries.setData(chartData);
      chart.timeScale().fitContent();
    }

    // Signal UI
    const sideClass =
      signal.signal === "LONG" ? "signal-long" :
      signal.signal === "SHORT" ? "signal-short" : "signal-wait";
    const p = signal.plan || {};
    const ind = signal.indicators || {};

    let html = `
      <div class="mini-label">${signal.symbol} · ${signal.timeframe}</div>
      <div class="signal-main ${sideClass}">${signal.signal}</div>
      <div class="signal-meta">
        <div>Model score: <b>${(signal.score * 100).toFixed(0)}%</b> <small style="color:var(--muted)">(not a guaranteed probability)</small></div>
        <div>Price: <b>${Number(signal.price).toFixed(4)}</b></div>
        <div>Entry: <b>${p.entry ?? "—"}</b></div>
        <div>Stop Loss: <b>${p.stop_loss ?? "—"}</b></div>
        <div>TP1 / TP2 / TP3: <b>${p.tp1 ?? "—"}</b> / <b>${p.tp2 ?? "—"}</b> / <b>${p.tp3 ?? "—"}</b></div>
        <div>R:R (TP2): <b>${p.risk_reward_tp2 ?? "—"}</b></div>
        <div>Validity: <b>~${signal.duration_minutes} min</b></div>
        <div>RSI: <b>${ind.rsi ?? "—"}</b> · ADX: <b>${ind.adx ?? "—"}</b></div>
      </div>
    `;

    if (signal.reasons && signal.reasons.length) {
      html += `<ul class="reasons">${signal.reasons.map((r) => `<li>${r}</li>`).join("")}</ul>`;
    }

    if (signal.ai_explanation) {
      html += `<div class="ai-box"><strong>AI Insight</strong><br>${signal.ai_explanation.replace(/\n/g, "<br>")}</div>`;
    }

    signalPanel.innerHTML = html;

    // Enable quick trade button if actionable
    const btn = document.getElementById("btnOpenFromSignal");
    if (btn) {
      btn.disabled = !(signal.signal === "LONG" || signal.signal === "SHORT") || !currentUser;
    }
  } catch (e) {
    console.error(e);
    signalPanel.innerHTML = "<p>Failed to load market data.</p>";
  }
}

// ---------- Demo Trading ----------
async function loadDemoAccount() {
  if (!authToken) return;
  try {
    const [accRes, tradesRes] = await Promise.all([
      fetch("/api/demo/account", { headers: authHeaders() }),
      fetch("/api/demo/trades?limit=20", { headers: authHeaders() }),
    ]);
    if (!accRes.ok) return;
    const acc = await accRes.json();
    const trades = tradesRes.ok ? await tradesRes.json() : [];

    document.getElementById("demoAccount").innerHTML = `
      <div class="stat-row"><span>Balance</span><b>$${acc.balance.toLocaleString()}</b></div>
      <div class="stat-row"><span>Equity</span><b>$${acc.equity.toLocaleString()}</b></div>
      <div class="stat-row"><span>Total P&L</span><b class="${acc.total_pnl >= 0 ? "pnl-pos" : "pnl-neg"}">$${acc.total_pnl.toFixed(2)}</b></div>
      <div class="stat-row"><span>Win / Loss</span><b>${acc.win_count} / ${acc.loss_count}</b></div>
      <div class="stat-row"><span>Win Rate</span><b>${acc.win_rate}%</b></div>
      <div class="stat-row"><span>Open Trades</span><b>${acc.open_trades_count}</b></div>
    `;

    if (trades.length === 0) {
      document.getElementById("tradeHistory").innerHTML = `<p class="muted">No trades yet. Open one from a signal.</p>`;
    } else {
      document.getElementById("tradeHistory").innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Symbol</th><th>Side</th><th>Entry</th><th>Status</th><th>P&L</th><th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${trades.map((t) => `
              <tr>
                <td>${t.symbol}</td>
                <td class="${t.side === "LONG" ? "pnl-pos" : "pnl-neg"}">${t.side}</td>
                <td>${Number(t.entry_price).toFixed(4)}</td>
                <td>${t.status}</td>
                <td class="${t.pnl >= 0 ? "pnl-pos" : "pnl-neg"}">${t.is_open ? "—" : "$" + t.pnl.toFixed(2)}</td>
                <td>${t.is_open ? `<button class="btn ghost" style="padding:4px 10px;font-size:12px;" onclick="closeTrade(${t.id}, ${t.entry_price})">Close</button>` : "—"}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      `;
    }
  } catch (e) {
    console.error(e);
  }
}

async function openTradeFromSignal() {
  if (!currentUser || !currentSignal || !currentSignal.plan) {
    alert("Login and generate a LONG/SHORT signal first.");
    return;
  }
  const p = currentSignal.plan;
  const qty = prompt("Quantity (e.g. 0.01 for BTC):", "0.01");
  if (!qty || isNaN(qty) || Number(qty) <= 0) return;

  try {
    const res = await fetch("/api/demo/trades", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({
        symbol: currentSignal.symbol,
        side: currentSignal.signal,
        entry_price: p.entry,
        stop_loss: p.stop_loss,
        tp1: p.tp1,
        tp2: p.tp2,
        tp3: p.tp3,
        quantity: Number(qty),
        signal_score: currentSignal.score,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to open trade");
    alert("Demo trade opened!");
    loadDemoAccount();
  } catch (e) {
    alert(e.message);
  }
}

async function closeTrade(tradeId, fallbackPrice) {
  const price = prompt("Exit price:", String(fallbackPrice));
  if (!price || isNaN(price)) return;
  try {
    const res = await fetch(`/api/demo/trades/${tradeId}/close`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ exit_price: Number(price), status: "CLOSED" }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to close");
    alert(`Closed. P&L: $${data.pnl}`);
    loadDemoAccount();
  } catch (e) {
    alert(e.message);
  }
}

// ---------- Blog ----------
async function loadBlogPosts() {
  const container = document.getElementById("blogTopics");
  try {
    const res = await fetch("/api/blog/posts?limit=30");
    const posts = await res.json();
    if (!posts.length) {
      // fallback to topics
      const tRes = await fetch("/api/blog/topics");
      const tData = await tRes.json();
      container.innerHTML = tData.topics.map((topic, i) => `
        <article class="glass blog-item">
          <div class="mini-label">TOPIC ${String(i + 1).padStart(2, "0")}</div>
          <h3>${topic}</h3>
          <p>SEO-ready educational topic. Generate full articles with Gemini after login.</p>
        </article>
      `).join("");
      return;
    }
    container.innerHTML = posts.map((p) => `
      <article class="glass blog-item">
        <div class="mini-label">${p.category || "Education"} · ${p.reading_time_minutes || 5} min</div>
        <h3>${p.title}</h3>
        <p>${p.excerpt || p.meta_description || ""}</p>
      </article>
    `).join("");
  } catch (e) {
    console.error(e);
  }
}

async function generateBlogs() {
  if (!authToken) {
    openModal("login");
    return;
  }
  const btn = document.getElementById("btnGenerateBlogs");
  btn.disabled = true;
  btn.textContent = "Generating...";
  try {
    const res = await fetch("/api/blog/generate?count=3", {
      method: "POST",
      headers: authHeaders(),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Generation failed");
    alert(`Generated ${data.count} article(s).`);
    loadBlogPosts();
  } catch (e) {
    alert(e.message + "\n\nMake sure GEMINI_API_KEY is set in .env");
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate AI Articles";
  }
}

// ---------- Pricing ----------
async function loadPlans() {
  try {
    const res = await fetch("/api/auth/plans");
    const plans = await res.json();
    const grid = document.getElementById("pricingGrid");
    grid.innerHTML = plans.map((p) => `
      <div class="glass price-card">
        <h3>${p.name}</h3>
        <div class="price">$${p.price_monthly}<span>/mo</span></div>
        <ul>
          <li>${p.signals_per_day} signals / day</li>
          <li>Demo balance $${p.demo_balance.toLocaleString()}</li>
          <li>${p.has_ai_explanations ? "AI explanations included" : "Basic signals"}</li>
          <li>${p.description}</li>
        </ul>
        <button class="btn ${p.name === "pro" ? "primary" : "ghost"} full" onclick="openModal('register')">
          ${p.price_monthly === 0 ? "Start Free" : "Choose " + p.name}
        </button>
      </div>
    `).join("");
  } catch (e) {
    console.error(e);
  }
}

// ---------- Init ----------
document.addEventListener("DOMContentLoaded", () => {
  initChart();
  updateHeader();
  loadDashboard();
  loadBlogPosts();
  loadPlans();
  if (authToken) loadDemoAccount();
  setInterval(() => loadDashboard().catch(console.error), 60000);
});

// Close modal on overlay click
document.getElementById("authModal")?.addEventListener("click", (e) => {
  if (e.target.id === "authModal") closeModal();
});
