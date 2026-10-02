// Small client-side helper for the attendance dashboard.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach(form => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"], button:not([type])');
      if (button && !form.hasAttribute("onsubmit")) {
        button.dataset.originalText = button.textContent;
      }
    });
  });
});
