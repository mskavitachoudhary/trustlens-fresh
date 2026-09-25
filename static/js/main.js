/* ==========================================================================
   TrustLens - main frontend behaviour
   Particles, navbar scroll, scroll-reveal, counters, result gauges and the
   shared API helper used by every scanner page.
   ========================================================================== */

(function () {
  "use strict";

  /* ---- Navbar scrolled state ------------------------------------------- */
  function onScroll() {
    const nav = document.querySelector(".navbar-trust");
    if (nav) nav.classList.toggle("scrolled", window.scrollY > 24);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---- Auto-dismiss flash alerts --------------------------------------- */
  document.querySelectorAll(".alert-trust").forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = "opacity .5s ease";
      alert.style.opacity = "0";
      setTimeout(function () { alert.remove(); }, 550);
    }, 4200);
  });

  /* ---- Scroll reveal ---------------------------------------------------- */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("visible"); });
  }

  /* ---- Animated counters ----------------------------------------------- */
  function animateCount(el) {
    const target = parseFloat(el.dataset.count || "0");
    const decimals = (el.dataset.count || "").includes(".") ? 1 : 0;
    const duration = 1200;
    const start = performance.now();
    function tick(now) {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (p < 1) requestAnimationFrame(tick);
      else el.textContent = target.toFixed(decimals);
    }
    requestAnimationFrame(tick);
  }

  const counters = document.querySelectorAll("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    const cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          cio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---- Shared API helper ------------------------------------------------ */
  window.TrustLens = {
    toggleTheme: function () {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("trustlens-theme", next);
      return next;
    },

    apiPost: function (url, data, isFormData) {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
      const headers = { "X-Requested-With": "XMLHttpRequest" };
      if (csrfToken) {
        headers["X-CSRFToken"] = csrfToken;
      }
      const opts = { method: "POST", headers: headers };
      if (isFormData) {
        if (data instanceof FormData && csrfToken && !data.has("csrf_token")) {
          data.append("csrf_token", csrfToken);
        }
        opts.body = data; // FormData sets its own multipart content-type
      } else {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(data);
      }
      return fetch(url, opts).then(function (res) {
        return res.json().then(function (json) {
          if (!res.ok || json.success === false) {
            const err = new Error(json.error || "Request failed.");
            err.status = res.status;
            throw err;
          }
          return json;
        });
      });
    },

    showError: function (box, message) {
      if (!box) return;
      box.innerHTML = "";
      box.classList.remove("result-hidden");
      box.classList.add("glass", "p-4");
      box.innerHTML =
        '<div class="d-flex align-items-start gap-3">' +
        '<span class="text-danger flex-shrink-0" style="margin-top:2px;">' +
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>' +
        '</span>' +
        '<div><h5 class="mb-1" style="color:var(--trust-danger)">Scan error</h5>' +
        '<p class="text-muted-c mb-0">' + escapeHtml(message) + "</p></div></div>";
      box.scrollIntoView({ behavior: "smooth", block: "nearest" });
    },

    loading: function (btn, text) {
      btn.disabled = true;
      const original = btn.dataset.original || btn.innerHTML;
      btn.dataset.original = original;
      btn.innerHTML =
        '<span class="spin-orb"></span> ' + (text || "Scanning...");
      return btn;
    },

    doneLoading: function (btn) {
      btn.disabled = false;
      if (btn.dataset.original) btn.innerHTML = btn.dataset.original;
    },

    /* Build a circular trust gauge. score 0-100 */
    renderGauge: function (container, score) {
      const ring = document.createElement("div");
      ring.className = "gauge-ring";
      const color =
        score >= 70 ? "var(--green)" : score >= 45 ? "var(--yellow)" : "var(--red)";
      ring.style.setProperty("--ring-color", color);
      ring.style.setProperty("--value", score);
      ring.innerHTML =
        '<div class="gauge-inner">' +
        '<div class="gauge-num">' + score + '</div>' +
        '<div class="gauge-label">TRUST SCORE</div></div>';
      container.innerHTML = "";
      container.appendChild(ring);
    },

    /* Risk gauge for the email scanner - higher score = MORE dangerous.
       Colour semantics are the inverse of the trust gauge above. */
    renderRiskGauge: function (container, score, label) {
      const ring = document.createElement("div");
      ring.className = "gauge-ring gauge-risk";
      const color =
        score >= 70 ? "var(--red)" : score >= 45 ? "var(--yellow)" : "var(--green)";
      ring.style.setProperty("--ring-color", color);
      ring.style.setProperty("--value", score);
      ring.innerHTML =
        '<div class="gauge-inner">' +
        '<div class="gauge-num">' + score + '</div>' +
        '<div class="gauge-label">' + (label || "RISK SCORE") + '</div></div>';
      container.innerHTML = "";
      container.appendChild(ring);
    },

    /* Status pill carrying a human-readable risk label + emoji, e.g. "Suspicious". */
    renderRiskPill: function (status, label, emoji) {
      const cls =
        status === "safe" ? "badge-safe" : status === "warning" ? "badge-warning" : "badge-dangerous";
      return '<span class="status-pill ' + cls + '">' +
        (emoji ? emoji + " " : "") + escapeHtml(label || (status || "").toUpperCase()) +
        "</span>";
    },

    renderStatusPill: function (status) {
      const labels = { safe: "SAFE", warning: "WARNING", dangerous: "DANGEROUS" };
      const cls =
        status === "safe" ? "badge-safe" : status === "warning" ? "badge-warning" : "badge-dangerous";
      return '<span class="status-pill ' + cls + '">' + (labels[status] || status.toUpperCase()) + "</span>";
    },

    renderReasons: function (list, reasons) {
      list.innerHTML = "";
      (reasons || []).forEach(function (r) {
        const li = document.createElement("li");
        li.className = "r-" + (r.severity || "info");
        li.innerHTML = '<span class="dot"></span><span>' + escapeHtml(r.text) + "</span>";
        list.appendChild(li);
      });
    },

    renderDetails: function (box, details) {
      if (!box) return;
      box.innerHTML = "";
      Object.keys(details || {}).forEach(function (key) {
        let value = details[key];
        if (value === true) value = "Yes";
        else if (value === false) value = "No";
        if (value === null || value === undefined || value === "") return;
        const chip = document.createElement("span");
        chip.className = "detail-chip";
        chip.innerHTML =
          "<strong>" + escapeHtml(String(key).replace(/_/g, " ")) + ":</strong> " +
          escapeHtml(String(value).substring(0, 90));
        box.appendChild(chip);
      });
    },

    showResult: function (box, data) {
      box.classList.remove("result-hidden");
      box.scrollIntoView({ behavior: "smooth", block: "nearest" });
    },

    /* Prominent "BLACKLISTED / UNSAFE" warning box shown when a scan matches
       a threat record. Renders above the gauge and reasons. */
    renderBlacklistBanner: function (parent, blacklisted, reason) {
      if (!parent) return;
      const existing = parent.querySelector(".blacklist-banner");
      if (existing) existing.remove();
      if (!blacklisted) return;
      const banner = document.createElement("div");
      banner.className = "blacklist-banner";
      banner.innerHTML =
        '<div class="blacklist-banner-icon">' +
        '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>' +
        '</div>' +
        '<div>' +
        '<div class="blacklist-banner-title">BLACKLISTED / UNSAFE</div>' +
        '<div class="blacklist-banner-text">' +
        "This address matches a known threat record in the TrustLens blacklist." +
        (reason ? " Reason: " + escapeHtml(reason) : "") +
        "</div></div>";
      parent.insertBefore(banner, parent.firstChild);
    }
  };

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = String(str == null ? "" : str);
    return div.innerHTML;
  }
  window.__escapeHtml = escapeHtml;

  /* ---- File drop zones -------------------------------------------------- */
  document.querySelectorAll(".drop-zone").forEach(function (zone) {
    const input = zone.querySelector('input[type="file"]');
    const label = zone.querySelector(".dz-filename");

    function formatFileLabel(files) {
      if (!files || !files.length) return "No file chosen";
      if (files.length === 1) {
        const f = files[0];
        const sizeStr = f.size > 1048576 ? (f.size / 1048576).toFixed(1) + " MB" : (f.size / 1024).toFixed(0) + " KB";
        return f.name + " (" + sizeStr + ")";
      }
      return files.length + " files selected";
    }

    if (input) {
      zone.addEventListener("click", function (e) {
        if (e.target !== input) input.click();
      });
      zone.addEventListener("dragover", function (e) {
        e.preventDefault();
        zone.classList.add("dragover");
      });
      zone.addEventListener("dragleave", function () { zone.classList.remove("dragover"); });
      zone.addEventListener("drop", function (e) {
        e.preventDefault();
        zone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
          input.files = e.dataTransfer.files;
          if (label) label.textContent = formatFileLabel(e.dataTransfer.files);
        }
      });
      input.addEventListener("change", function () {
        if (label && input.files.length) label.textContent = formatFileLabel(input.files);
      });
    }
  });

  /* ---- Theme switcher --------------------------------------------------- */
  function initThemeToggle() {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("trustlens-theme", next);
    });
    if (window.matchMedia) {
      window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
        if (!localStorage.getItem("trustlens-theme")) {
          document.documentElement.setAttribute("data-theme", e.matches ? "dark" : "light");
        }
      });
    }
  }
  initThemeToggle();

  /* ---- Dashboard charts (lightweight canvas bars) ----------------------- */
  function drawBars(canvas, values, colors) {
    if (!canvas || !values.length) return;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.offsetWidth, H = canvas.offsetHeight;
    canvas.width = W * dpr; canvas.height = H * dpr;
    ctx.scale(dpr, dpr);
    const max = Math.max.apply(null, values.concat([1]));
    const gap = 10, barW = (W - gap * (values.length - 1)) / values.length;
    values.forEach(function (v, i) {
      const bh = Math.max(4, (v / max) * (H - 14));
      const x = i * (barW + gap);
      const y = H - bh;
      const grad = ctx.createLinearGradient(0, y, 0, H);
      grad.addColorStop(0, colors[i] || "#7c5cff");
      grad.addColorStop(1, "rgba(124, 92, 255, 0.15)");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.roundRect(x, y, barW, bh, [6, 6, 0, 0]);
      ctx.fill();
    });
  }
  window.TrustLens.drawBars = drawBars;
})();
