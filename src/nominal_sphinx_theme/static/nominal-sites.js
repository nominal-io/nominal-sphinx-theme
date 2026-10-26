// The docs-site menu after the Nominal logo (templates/nominal/sites.html), on the docs and the hub's
// landing pages alike: its button opens and closes it, and a click elsewhere or Escape closes it.
(() => {
  const setup = () => {
    for (const root of document.querySelectorAll("[data-nominal-sites]")) {
      const button = root.querySelector("button");
      const menu = root.querySelector("ul");
      const open = (yes) => {
        menu.hidden = !yes;
        button.setAttribute("aria-expanded", String(yes));
      };
      button.addEventListener("click", () => open(menu.hidden));
      document.addEventListener("click", (event) => {
        if (!root.contains(event.target)) open(false);
      });
      document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape" || menu.hidden) return;
        open(false);
        button.focus();
      });
    }
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})();
