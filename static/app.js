"use strict";

const state = { expr: "", last: "", error: "", fresh: false, busy: false };

const els = {
  expr: document.getElementById("expr"),
  last: document.getElementById("last"),
  error: document.getElementById("error"),
  keypad: document.getElementById("keypad"),
};

const INSERTABLE = /^[0-9+\-*\/^%().,]$/;
const PRETTY = { "*": "\u00d7", "/": "\u00f7", "-": "\u2212" };

function pretty(text) {
  return text.replace(/[*\/-]/g, (c) => PRETTY[c]);
}

function render() {
  els.expr.textContent = state.expr ? pretty(state.expr) : "0";
  els.expr.classList.toggle("small", state.expr.length > 14);
  els.last.textContent = state.last;
  els.error.textContent = state.error;
}

function press(key) {
  state.error = "";
  // After a result, typing a number or function starts a new calculation;
  // typing an operator continues from the result.
  if (state.fresh && /^[0-9.(a-z]/i.test(key)) {
    state.expr = "";
    state.last = "";
  }
  state.fresh = false;
  state.expr += key;
  render();
}

function backspace() {
  state.error = "";
  state.fresh = false;
  state.expr = state.expr.slice(0, -1);
  render();
}

function clearAll() {
  state.expr = "";
  state.last = "";
  state.error = "";
  state.fresh = false;
  render();
}

async function calculate() {
  if (!state.expr || state.busy) return;
  state.busy = true;
  try {
    const res = await fetch("/api/evaluate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression: state.expr }),
    });
    const data = await res.json();
    if (data.ok) {
      state.last = pretty(state.expr) + " =";
      // Scientific notation (1e-7) cannot be re-used as input, so show it only above.
      state.expr = /e/i.test(data.display) ? "" : data.display;
      if (!state.expr) state.last += " " + data.display;
      state.error = "";
      state.fresh = true;
      loadHistory();
    } else {
      state.error = data.error;
    }
  } catch (err) {
    state.error = "Something went wrong. Please try again.";
  } finally {
    state.busy = false;
  }
  render();
}

els.keypad.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  if (btn.dataset.action === "clear") clearAll();
  else if (btn.dataset.action === "back") backspace();
  else if (btn.dataset.action === "equals") calculate();
  else if (btn.dataset.key) press(btn.dataset.key);
});

document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  if (e.key === "Enter" || e.key === "=") {
    e.preventDefault();
    calculate();
  } else if (e.key === "Backspace") {
    backspace();
  } else if (e.key === "Escape") {
    clearAll();
  } else if (INSERTABLE.test(e.key)) {
    press(e.key);
  }
});

render();

/* ---------- History (stored in SQLite, served by /api/history) ---------- */

const historyEls = {
  list: document.getElementById("history-list"),
  clear: document.getElementById("history-clear"),
};

async function loadHistory() {
  try {
    const res = await fetch("/api/history?limit=30");
    const data = await res.json();
    renderHistory(data.items || []);
  } catch (err) {
    // History is a convenience; the calculator still works without it.
  }
}

function renderHistory(items) {
  historyEls.list.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("li");
    empty.className = "history-empty";
    empty.textContent = "No calculations yet.";
    historyEls.list.append(empty);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "history-item";
    btn.type = "button";
    btn.dataset.expression = item.expression;
    const expr = document.createElement("span");
    expr.className = "h-expr";
    expr.textContent = pretty(item.expression);
    const result = document.createElement("span");
    result.className = "h-res";
    result.textContent = "= " + item.display;
    btn.append(expr, result);
    li.append(btn);
    historyEls.list.append(li);
  }
}

historyEls.list.addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  state.expr = btn.dataset.expression;
  state.error = "";
  state.fresh = false;
  render();
});

historyEls.clear.addEventListener("click", async () => {
  try {
    await fetch("/api/history", { method: "DELETE" });
  } finally {
    loadHistory();
  }
});

/* ---------- Theme ---------- */

const themeToggle = document.getElementById("theme-toggle");

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  themeToggle.textContent = theme === "dark" ? "\u2600" : "\u263e";
  themeToggle.setAttribute("aria-label", "Switch to " + (theme === "dark" ? "light" : "dark") + " theme");
}

function initTheme() {
  let saved = null;
  try {
    saved = localStorage.getItem("calclab-theme");
  } catch (err) {
    // Storage can be unavailable (private mode); fall back to the OS preference.
  }
  const prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
  applyTheme(saved || (prefersLight ? "light" : "dark"));
}

themeToggle.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  try {
    localStorage.setItem("calclab-theme", next);
  } catch (err) {
    // Ignore: the theme simply will not persist.
  }
});

initTheme();
loadHistory();
