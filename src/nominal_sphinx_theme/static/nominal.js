// Header links (Guides, Forum, social icons) leave the docs, so open them in a new tab.
document.addEventListener("DOMContentLoaded", () => {
  for (const a of document.querySelectorAll('.sy-head a[href^="http"]')) {
    a.target = "_blank";
    a.rel = "noopener";
  }
});


// The Nominal logo links to the hub's /{lang}/ folder, which redirects to the landing page with that
// language's card open (index.html#python). Go straight there instead, saving a page load (and its
// flash); without JavaScript the link still works through the redirect.
document.addEventListener("DOMContentLoaded", () => {
  const a = document.querySelector("a.nominal-hub[data-hub-lang]");
  if (!a) return;
  const url = new URL(a.href); // .../python/, or .../python/index.html in an offline copy
  const lang = url.pathname.replace(/index\.html$/, "").replace(/\/+$/, "").split("/").pop();
  if (!lang) return;
  const landing = new URL("../", url); // the folder above /python/ (or above python/index.html)
  a.href = landing.href + (url.protocol === "file:" ? "index.html" : "") + "#" + lang;
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
// with each group open or folded to start); a click opens or closes the group under it.
document.addEventListener("click", (event) => {
  const button = event.target.closest("button.nominal-fold");
  if (!button) return;
  const open = button.getAttribute("aria-expanded") !== "true";
  button.setAttribute("aria-expanded", String(open));
  button.parentElement.nextElementSibling.hidden = !open;
});
