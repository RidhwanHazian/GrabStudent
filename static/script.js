document.addEventListener("DOMContentLoaded", () => {

  // ----------------- Flash / Success Messages -----------------
  const msg = document.querySelector(".success-msg");
  if (msg && msg.textContent.trim() !== "") {
    msg.style.display = "block";
    setTimeout(() => { msg.style.display = "none"; }, 5000);
  }

  // ----------------- Admin Chart -----------------
  const completedEl = document.getElementById('completed_count');
  const pendingEl = document.getElementById('pending_count');
  const cancelledEl = document.getElementById('cancelled_count');

  if (completedEl && pendingEl && cancelledEl) {
    const completed = parseInt(completedEl.innerText);
    const pending = parseInt(pendingEl.innerText);
    const cancelled = parseInt(cancelledEl.innerText);

    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Completed', 'Pending', 'Cancelled'],
        datasets: [{
          data: [completed, pending, cancelled],
          backgroundColor: ['#a3be8c', '#ebcb8b', '#bf616a'],
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' },
          title: { display: true, text: 'Booking Status Overview' }
        }
      }
    });
  }

  // ----------------- Hamburger Menu Toggle -----------------
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      if (window.innerWidth <= 600) navLinks.classList.toggle('active');
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 600) navLinks.classList.remove('active');
    });
  }

});
