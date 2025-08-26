// Show success message
function showMessage(msgId, text) {
    const msg = document.getElementById(msgId);
    msg.innerText = text;
    msg.style.display = "block";

    setTimeout(() => {
        msg.style.display = "none";
    }, 5000);
}

// Booking form
const bookingForm = document.querySelector('form[onsubmit="submitBooking(event)"]');
if (bookingForm) {
    bookingForm.addEventListener('submit', function(event) {
        event.preventDefault();
        showMessage("message", "✅ Booking submitted successfully (demo only, not saved).");
    });
}

// Login form
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();
        showMessage("login-message", "✅ Login successful (demo only, not saved).");
    });
}

// Toggle mobile menu
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        if (window.innerWidth <= 600) {
            navLinks.classList.toggle('active');
        }
    });
}

// Optional: Close menu if window resized above 600px
window.addEventListener('resize', () => {
    if (window.innerWidth > 600) {
        navLinks.classList.remove('active');
    }
});
