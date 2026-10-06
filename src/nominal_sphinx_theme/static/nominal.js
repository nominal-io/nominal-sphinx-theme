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
