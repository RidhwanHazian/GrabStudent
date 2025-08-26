// Show flash/success messages
document.addEventListener("DOMContentLoaded", () => {
  const msg = document.querySelector(".success-msg");
  if(msg && msg.textContent.trim() !== "") {
    msg.style.display = "block";
    setTimeout(() => { msg.style.display = "none"; }, 5000);
  }

  // Handle "Other" pickup input
  const pickupSelect = document.getElementById("pickup");
  const otherInput = document.getElementById("other_location");

  if (pickupSelect && otherInput) {
    otherInput.style.display = "none";
    otherInput.required = false;

    pickupSelect.addEventListener("change", () => {
      if (pickupSelect.value === "Other") {
        otherInput.style.display = "block";
        otherInput.required = true;
      } else {
        otherInput.style.display = "none";
        otherInput.required = false;
      }
    });
  }
});

// Booking form demo message (optional for testing)
const bookingForm = document.querySelector('form[onsubmit="submitBooking(event)"]');
if (bookingForm) {
  bookingForm.addEventListener('submit', function(event) {
    event.preventDefault();
    showMessage("message", "✅ Booking submitted successfully (demo only, not saved).");
  });
}

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
