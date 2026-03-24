// ============================================
// Career Path Explorer — Client-side JS
// ============================================

// Highlight the active nav link based on current page
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  document.querySelectorAll("nav ul a").forEach(a => {
    if (a.getAttribute("href") === path) {
      a.style.color = "var(--accent)";
      a.style.fontWeight = "700";
    }
  });

  // Animate cards in on load
  document.querySelectorAll(".card").forEach((card, i) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    card.style.transition = `opacity .4s ease ${i * 60}ms, transform .4s ease ${i * 60}ms`;
    setTimeout(() => {
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, 50);
  });
});
