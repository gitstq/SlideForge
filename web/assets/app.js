/* SlideForge — 前端逻辑 */
(() => {
  "use strict";

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  const state = {
    themes: [],
    theme: "ocean",
    previews: [],
    slide: 0,
    pptxBase64: null,
    filename: "slideforge.pptx",
  };

  const stage = $("#stage");
  const slideFrame = $("#slideFrame");
  const loading = $("#loading");
  const emptyState = $("#emptyState");

  // ---------- 初始化 ----------
  async function init() {
    bindReveal();
    bindNav();
    try {
      const [themes, providers] = await Promise.all([
        fetch("/api/themes").then((r) => r.json()),
        fetch("/api/providers").then((r) => r.json()),
      ]);
      state.themes = themes;
      renderSwatches(themes);
      renderProviders(providers);
      const sample = await fetch("/api/sample-outline").then((r) => r.json());
      state.sample = sample;
    } catch (e) {
      console.warn("init", e);
    }

    $("#form").addEventListener("submit", onGenerate);
    $("#demoBtn").addEventListener("click", onDemo);
    $("#prevBtn").addEventListener("click", () => nav(-1));
    $("#nextBtn").addEventListener("click", () => nav(1));
    $("#slides").addEventListener("input", (e) => {
      $("#slidesOut").textContent = e.target.value + " 页";
    });

    // 载入主题默认值
    const provider = $("#provider");
    if (provider && provider.value) applyProviderDefaults();
    provider && provider.addEventListener("change", applyProviderDefaults);
  }

  function renderSwatches(themes) {
    const box = $("#swatches");
    box.innerHTML = "";
    themes.forEach((t) => {
      const el = document.createElement("button");
      el.type = "button";
      el.className = "swatch" + (t.id === state.theme ? " active" : "");
      el.style.background = t.accent;
      el.title = t.name;
      el.dataset.id = t.id;
      el.addEventListener("click", () => {
        state.theme = t.id;
        $$(".swatch").forEach((s) => s.classList.remove("active"));
        el.classList.add("active");
      });
      box.appendChild(el);
    });
  }

  function renderProviders(providers) {
    const sel = $("#provider");
    sel.innerHTML = "";
    providers.forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = `${p.name}（${p.model}）`;
      sel.appendChild(opt);
    });
  }

  function applyProviderDefaults() {
    // 模型 / base-url 留空则交给服务端默认；这里仅提示
    const base = $("#baseUrl");
    const model = $("#model");
    if (!base.value) base.placeholder = "使用该模型商默认端点";
    if (!model.value) model.placeholder = "使用该模型商默认模型";
  }

  // ---------- 生成 ----------
  function payload() {
    return {
      topic: $("#topic").value.trim() || "未命名主题",
      provider: $("#provider").value,
      api_key: $("#apiKey").value.trim(),
      base_url: $("#baseUrl").value.trim() || null,
      model: $("#model").value.trim() || null,
      theme: state.theme,
      slides: Number($("#slides").value),
      effect: $("#effect").value,
      transition: $("#transition").value,
    };
  }

  async function onGenerate(ev) {
    ev.preventDefault();
    await run(payload());
  }

  async function onDemo() {
    if (!state.sample) {
      alert("示例大纲尚未加载，请稍后再试。");
      return;
    }
    await run({ outline: state.sample });
  }

  async function run(body) {
    setLoading(true);
    try {
      const resp = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || "生成失败");

      state.previews = data.previews || [];
      state.slide = 0;
      state.pptxBase64 = data.pptx_base64;
      state.filename = data.filename || "slideforge.pptx";
      state.title = data.title || "";

      emptyState.classList.add("hidden");
      slideFrame.classList.remove("hidden");
      renderSlide();
      renderThumbs();
      bindDownload();
    } catch (e) {
      alert("生成失败：" + e.message);
    } finally {
      setLoading(false);
    }
  }

  function setLoading(on) {
    loading.classList.toggle("hidden", !on);
    slideFrame.classList.toggle("hidden", on && !state.previews.length);
    emptyState.classList.toggle("hidden", on || state.previews.length > 0);
    $("#generateBtn").disabled = on;
    const label = $("#generateBtn .btn-label");
    if (label) label.textContent = on ? "锻造中…" : "锻造生成 .pptx";
  }

  function renderSlide() {
    const svg = state.previews[state.slide];
    if (!svg) return;
    slideFrame.innerHTML = svg;
    $("#pageInfo").textContent = `${state.slide + 1} / ${state.previews.length}`;
    $$(".thumb").forEach((t, i) => t.classList.toggle("active", i === state.slide));
    // 预览切换动效
    slideFrame.style.opacity = 0;
    requestAnimationFrame(() => {
      slideFrame.style.transition = "opacity 0.25s";
      slideFrame.style.opacity = 1;
    });
  }

  function renderThumbs() {
    const box = $("#thumbs");
    box.innerHTML = "";
    state.previews.forEach((svg, i) => {
      const t = document.createElement("div");
      t.className = "thumb" + (i === 0 ? " active" : "");
      t.innerHTML = svg;
      t.addEventListener("click", () => {
        state.slide = i;
        renderSlide();
      });
      box.appendChild(t);
    });
  }

  function nav(delta) {
    if (!state.previews.length) return;
    state.slide = (state.slide + delta + state.previews.length) % state.previews.length;
    renderSlide();
  }

  function bindDownload() {
    const btn = $("#downloadBtn");
    if (!state.pptxBase64) return;
    const bin = atob(state.pptxBase64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const blob = new Blob([bytes], { type: "application/vnd.openxmlformats-officedocument.presentationml.presentation" });
    btn.href = URL.createObjectURL(blob);
    btn.download = state.filename;
  }

  // ---------- 滚动入场 ----------
  function bindReveal() {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          en.target.classList.add("in");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12 });
    $$(".reveal").forEach((el) => io.observe(el));
  }

  function bindNav() {
    const links = $$('a[href^="#"]');
    links.forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href");
        if (id.length > 1 && $(id)) {
          e.preventDefault();
          $(id).scrollIntoView({ behavior: "smooth" });
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
