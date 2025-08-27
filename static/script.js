// Show flash/success messages
document.addEventListener("DOMContentLoaded", () => {
  const msg = document.querySelector(".success-msg");
  if(msg && msg.textContent.trim() !== "") {
    msg.style.display = "block";
    setTimeout(() => { msg.style.display = "none"; }, 5000);
  }
});

// Login form demo message (optional for testing)
const loginForm = document.getElementById('login-form');
if (loginForm) {
  loginForm.addEventListener('submit', function(event) {
    event.preventDefault();
    showMessage("login-message", "✅ Login successful (demo only, not saved).");
  });
}

// Toggle mobile hamburger menu
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    if (window.innerWidth <= 600) {
      navLinks.classList.toggle('active');
    }
  });
}

// Optional: Close mobile menu if window resized above 600px
window.addEventListener('resize', () => {
  if (navLinks && window.innerWidth > 600) {
    navLinks.classList.remove('active');
  }
});
