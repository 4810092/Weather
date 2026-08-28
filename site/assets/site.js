const header = document.querySelector("[data-header]");
const toggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");

const updateHeader = () => header?.classList.toggle("is-scrolled", window.scrollY > 8);
updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

toggle?.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded", String(open));
  nav?.classList.toggle("is-open", open);
});

nav?.addEventListener("click", (event) => {
  if (event.target instanceof HTMLAnchorElement && toggle) {
    toggle.setAttribute("aria-expanded", "false");
    nav.classList.remove("is-open");
  }
});
