// Players: each <figure data-clip="id"> gets its video's inputs drawn as a piano roll that follows the playhead,
// a frame counter, and the task's steps as chips that light up when their predicate first holds.
(function () {
  const DATA = JSON.parse(document.getElementById("clip-data").textContent);
  const BTN = { U: 0x10, D: 0x20, L: 0x40, R: 0x80, A: 0x01, B: 0x02, S: 0x04, T: 0x08 };
  const ROWS = [["←", 0x40], ["→", 0x80], ["↑", 0x10], ["↓", 0x20], ["B", 0x02], ["A", 0x01]];
  function parse(spec) {
    const out = [];
    for (const tok of spec.trim().split(/\s+/)) {
      const [b, n] = tok.split("*");
      let m = 0;
      for (const ch of b) if (BTN[ch]) m |= BTN[ch];
      const k = n ? parseInt(n, 10) : 1;
      for (let i = 0; i < k; i++) out.push(m);
    }
    return out;
  }
  document.querySelectorAll("figure[data-clip]").forEach((fig) => {
    const d = DATA[fig.dataset.clip];
    if (!d) return;
    const video = fig.querySelector("video");
    const canvas = fig.querySelector("canvas.strip");
    const frameEl = fig.querySelector(".frame");
    const heldEl = fig.querySelector(".held-now");
    const chips = [...fig.querySelectorAll(".steps button")];
    const masks = d.spec ? parse(d.spec) : null;
    const fps = d.fps || 60.0988;
    chips.forEach((c) => c.addEventListener("click", () => {
      video.currentTime = Math.max(0, (parseInt(c.dataset.frame, 10) - d.start - 45) / fps);
      video.play().catch(() => {});
    }));
    function draw() {
      const f = Math.min((d.end || 1e9) - d.start - 1, Math.max(0, Math.round(video.currentTime * fps)));
      const abs = d.start + f;
      if (frameEl) frameEl.textContent = "FRAME " + String(abs).padStart(5, "0");
      chips.forEach((c) => c.classList.toggle("held", abs >= parseInt(c.dataset.frame, 10)));
      if (!canvas || !masks) return;
      const dpr = window.devicePixelRatio || 1;
      const w = canvas.clientWidth, h = canvas.clientHeight;
      if (canvas.width !== Math.round(w * dpr)) { canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr); }
      const g = canvas.getContext("2d");
      g.setTransform(dpr, 0, 0, dpr, 0, 0);
      g.clearRect(0, 0, w, h);
      const left = 26, rowH = (h - 14) / ROWS.length, px = Math.max(2, Math.min(4, (w - left) / 240));
      const span = Math.floor((w - left) / px), from = f - Math.floor(span * 0.35);
      g.font = "11px 'IBM Plex Mono', monospace"; g.textBaseline = "middle";
      ROWS.forEach(([label, bit], r) => {
        const y = r * rowH;
        g.fillStyle = "#151b38"; g.fillRect(left, y + 1, w - left, rowH - 2);
        g.fillStyle = "#8e9ac0"; g.fillText(label, 8, y + rowH / 2);
        g.fillStyle = r < 4 ? "#7db4ff" : "#ff8fb8";
        let run = -1;
        for (let i = 0; i <= span; i++) {
          const k = from + i, on = k >= 0 && k < masks.length && (masks[k] & bit);
          if (on && run < 0) run = i;
          if (!on && run >= 0) { g.fillRect(left + run * px, y + 2, (i - run) * px, rowH - 4); run = -1; }
        }
      });
      // step markers
      g.font = "9px 'IBM Plex Mono', monospace";
      (d.steps || []).forEach((s) => {
        const i = s.frame - d.start - from;
        if (i < 0 || i > span) return;
        g.fillStyle = "#8ee0a8"; g.fillRect(left + i * px, 0, 1.5, h - 14);
      });
      const xh = left + (f - from) * px;
      g.fillStyle = "#ffffff"; g.fillRect(xh, 0, 1.5, h - 12);
      g.fillStyle = "#8e9ac0"; g.textBaseline = "alphabetic";
      for (let k = Math.ceil(from / 60) * 60; k < from + span; k += 60) {
        if (k < 0) continue;
        g.fillRect(left + (k - from) * px, h - 13, 1, 3);
        if (((k / 60) | 0) % 2 === 0) g.fillText(String(d.start + k), left + (k - from) * px + 3, h - 2);
      }
      if (heldEl) {
        const m = masks[f] || 0;
        heldEl.textContent = "holding " + (ROWS.filter(([, b]) => m & b).map(([l]) => l).join(" ") || "nothing");
      }
    }
    let raf = 0;
    const loop = () => { draw(); raf = requestAnimationFrame(loop); };
    video.addEventListener("play", () => { cancelAnimationFrame(raf); loop(); });
    video.addEventListener("pause", () => { cancelAnimationFrame(raf); draw(); });
    video.addEventListener("seeked", draw);
    video.addEventListener("loadedmetadata", draw);
    window.addEventListener("resize", draw);
    draw();
  });

  // The exploration archive, replayed: cells appear in the iteration the search first reached them.
  document.querySelectorAll("canvas.archive").forEach((cv) => {
    const A = JSON.parse(document.getElementById(cv.dataset.src).textContent);
    if (!A.cells) return;
    const g = cv.getContext("2d");
    const T = 24, cols = A.cols, rows = Math.min(A.rows, 11), band = 30, LH = rows * T + band;
    cv.width = cols * T; cv.height = LH * 2;
    const maxIt = A.iters;
    const LABEL = ["Warp Star loaded", "Warp Star unloaded"];
    function paint(it) {
      g.fillStyle = "#0a0e1f"; g.fillRect(0, 0, cv.width, cv.height);
      const n = [0, 0];
      for (let layer = 0; layer < 2; layer++) {
        const oy = layer * LH + band;
        for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
          const t = A.grid[r][c];
          if (t === 1) { g.fillStyle = "#273158"; g.fillRect(c * T, oy + r * T, T, T); }
          else if (t === 2) { g.fillStyle = "#6a5a2c"; g.fillRect(c * T + 2, oy + r * T + 2, T - 4, T - 4); }
        }
        for (const [x, y, ns, born] of A.cells) {
          if (born > it || (ns ? 0 : 1) !== layer || y / 16 >= rows) continue;
          n[layer]++;
          g.fillStyle = layer ? "rgba(255,143,184,0.9)" : "rgba(125,180,255,0.85)";
          g.fillRect((x - A.x0) / 16 * T + 1, oy + y / 16 * T + 1, A.cw / 16 * T - 2, T - 2);
        }
        if (!layer) { g.fillStyle = "#ffd76a"; g.beginPath(); g.arc((A.star[0] - A.x0) / 16 * T, oy + A.star[1] / 16 * T, 7, 0, 7); g.fill(); }
        g.fillStyle = "#dfe5fa"; g.font = "500 13px 'IBM Plex Mono', monospace"; g.textBaseline = "middle";
        g.fillText(LABEL[layer] + " · " + n[layer] + " cells", 8, layer * LH + band / 2);
      }
      const lab = cv.parentElement.querySelector(".arch-it");
      if (lab) lab.textContent = "iteration " + it + " of " + maxIt + (it >= A.goal_it ? " · goal first reached on iteration " + A.goal_it : "");
    }
    paint(maxIt);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => paint(maxIt));
    const btn = cv.parentElement.querySelector("button.replay");
    if (btn) btn.addEventListener("click", () => {
      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { paint(maxIt); return; }
      const t0 = performance.now();
      (function step(now) { const it = Math.min(maxIt, Math.floor((now - t0) / 110)); paint(it); if (it < maxIt) requestAnimationFrame(step); })(t0);
    });
  });
})();
