// Header links (Guides, Forum, social icons) leave the docs, so open them in a new tab.
document.addEventListener("DOMContentLoaded", () => {
  for (const a of document.querySelectorAll('.sy-head a[href^="http"]')) {
    a.target = "_blank";
    a.rel = "noopener";
  }
});


// Each code block's bar (nominal.css) names its language, from its wrapper's highlight-<lang> class.
// Python's other lexer names show as "python"; blocks without a set language show none.
document.addEventListener("DOMContentLoaded", () => {
  const names = { python3: "python", py: "python", pycon: "python", ipython: "python", ipython3: "python", ps1: "powershell", pwsh: "powershell" };
  for (const block of document.querySelectorAll("div[class*='highlight-'] > div.highlight")) {
    const lang = [...block.parentElement.classList].find((c) => c.startsWith("highlight-"))?.slice("highlight-".length);
    if (lang && lang !== "default" && lang !== "none") block.dataset.lang = names[lang] ?? lang;
  }
});


// The "#" after each heading also copies a link to that section, so it can be pasted straight into
// a message. "Copied" shows beside it for a moment (nominal.css). The link still goes to the section.
document.addEventListener("DOMContentLoaded", () => {
  if (!navigator.clipboard) return;
  for (const a of document.querySelectorAll("a.headerlink")) a.title = "Copy link to this section";
});
document.addEventListener("click", (event) => {
  const a = event.target.closest("a.headerlink");
  if (!a || !navigator.clipboard) return;
  navigator.clipboard.writeText(a.href).then(() => {
    a.classList.add("nominal-copied");
    setTimeout(() => a.classList.remove("nominal-copied"), 1500);
  });
});


// With nominal_sidebar_open set, each sidebar group's caption is a button (rendered by the theme,
// with each group open or folded to start); a click opens or closes the group under it. Each button
// gets its own listener: Shibuya stops clicks inside the sidebar from reaching the document.
document.addEventListener("DOMContentLoaded", () => {
  for (const button of document.querySelectorAll("button.nominal-fold")) {
    button.addEventListener("click", () => {
      const open = button.getAttribute("aria-expanded") !== "true";
      button.setAttribute("aria-expanded", String(open));
      button.parentElement.nextElementSibling.hidden = !open;
    });
  }
});


// "On this page" highlights the entry for the heading the reader is at: the last heading at or above
// the top of the viewport (below the sticky header), or the last one at the bottom of the page.
// Shibuya marks entries `.active` by its own rules; this marks `.nominal-current` instead, which
// nominal.css styles. A clicked entry stays current until the reader scrolls by hand, because the
// page may be too short to bring its heading to the top.
document.addEventListener("DOMContentLoaded", () => {
  const toc = document.querySelector(".sy-rside .localtoc");
  if (!toc) return;
  const entries = [];
  for (const link of toc.querySelectorAll("a[href^='#']")) {
    const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (target) entries.push({ link, target });
  }
  if (!entries.length) return;

  // Shibuya's spy also scrolls the list to its own pick; shadowing its scroll call leaves that to
  // setCurrent below.
  for (const item of toc.querySelectorAll("li")) item.scrollIntoViewIfNeeded = null;

  let current = null;
  let pinned = null; // the entry the reader chose, until they scroll by hand

  const setCurrent = (entry) => {
    if (entry === current) return;
    current?.link.classList.remove("nominal-current");
    current?.link.removeAttribute("aria-current");
    current = entry;
    entry.link.classList.add("nominal-current");
    entry.link.setAttribute("aria-current", "true");
    const box = toc.closest(".sy-rside-inner");
    if (!box) return;
    const at = entry.link.getBoundingClientRect();
    const view = box.getBoundingClientRect();
    if (at.top < view.top) box.scrollTop -= view.top - at.top;
    else if (at.bottom > view.bottom) box.scrollTop += at.bottom - view.bottom;
  };

  const update = () => {
    if (pinned) return setCurrent(pinned);
    const atBottom = window.innerHeight + Math.round(window.scrollY) >= document.documentElement.scrollHeight;
    if (atBottom) return setCurrent(entries[entries.length - 1]);
    // An anchor jump puts the target at its scroll-margin-top, give or take a pixel.
    let found = entries[0];
    for (const entry of entries) {
      if (!entry.target.getClientRects().length) continue; // hidden, e.g. in a closed <details>
      const margin = parseFloat(getComputedStyle(entry.target).scrollMarginTop) || 0;
      if (entry.target.getBoundingClientRect().top > margin + 4) break;
      found = entry;
    }
    setCurrent(found);
  };

  const pin = (entry) => {
    pinned = entry;
    update();
  };
  const unpin = () => {
    pinned = null;
  };

  toc.addEventListener("click", (event) => {
    const entry = entries.find((e) => e.link === event.target.closest("a"));
    if (entry) pin(entry);
  });
  window.addEventListener("hashchange", () => {
    const entry = entries.find((e) => e.link.hash === location.hash);
    if (entry) pin(entry);
    else {
      unpin();
      update();
    }
  });
  for (const type of ["wheel", "touchmove", "keydown", "pointerdown"]) window.addEventListener(type, unpin, { passive: true });
  window.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);

  const landed = entries.find((e) => e.link.hash === location.hash);
  if (landed) pin(landed);
  else update();
});


// A button above "On this page" folds every code block on the page, and unfolds them again. A folded
// code block leaves a "Show code" bar that opens that block alone, and an open block has a "Fold"
// button, in the top right, that folds it again. Code a notebook hides on its own
// (the `hide-input` tag) is folded with the rest, and the button opens it too. The button reads "Fold
// all code" while any block is open and "Unfold all code" once every block is folded. It is not
// added to a page without code blocks.
document.addEventListener("DOMContentLoaded", () => {
  const toc = document.querySelector(".sy-rside .localtoc");
  if (!toc) return;

  // A plain code block goes inside a <details>, whose summary is the bar shown while it is folded.
  const folds = [];
  for (const block of document.querySelectorAll('main div[class*="highlight-"]')) {
    // Skip a cell's output (also highlighted), and a hidden notebook cell, which is handled below.
    if (block.closest(".cell_output, details")) continue;
    const fold = document.createElement("details");
    fold.className = "nominal-code";
    fold.open = true;
    const bar = document.createElement("summary");
    bar.textContent = "Show code";
    block.replaceWith(fold);
    fold.append(bar, block);
    // A "Fold" button in the top right, apart from the copy button, folds it alone.
    const foldOne = document.createElement("button");
    foldOne.type = "button";
    foldOne.className = "nominal-fold-one";
    foldOne.textContent = "Fold";
    foldOne.title = "Fold this code block";
    foldOne.addEventListener("click", () => {
      fold.open = false;
    });
    block.querySelector(".highlight")?.append(foldOne);
    folds.push(fold);
  }
  folds.push(...document.querySelectorAll("main details.hide.above-input"));
  if (!folds.length) return;

  const button = document.createElement("button");
  button.type = "button";
  button.className = "nominal-fold-all";
  const icon = (name, paths) =>
    `<svg class="${name}" viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" fill="none" stroke="currentColor" ` +
    `stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${paths}</svg>`;
  // Chevrons point in while code is open (a click folds it) and out once it is folded.
  button.innerHTML =
    icon("fold", '<path d="M4 3l4 3.5L12 3M4 13l4-3.5L12 13"/>') +
    icon("unfold", '<path d="M4 6.5L8 3l4 3.5M4 9.5L8 13l4-3.5"/>') +
    "<span></span>";
  toc.before(button); // above the list, not one of its entries

  const label = button.querySelector("span");
  const update = () => {
    const anyOpen = folds.some((fold) => fold.open);
    label.textContent = anyOpen ? "Fold all code" : "Unfold all code";
    button.classList.toggle("nominal-folded", !anyOpen);
  };
  // Each listener is its own: `toggle` does not bubble. Shibuya stops clicks in the sidebar from
  // reaching the document, so the button has its own too.
  for (const fold of folds) fold.addEventListener("toggle", update);
  button.addEventListener("click", () => {
    const open = !folds.some((fold) => fold.open);
    for (const fold of folds) fold.open = open;
    update();
  });
  update();
});
