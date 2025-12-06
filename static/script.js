// =======================
// Smooth Scroll for Navbar Links
// =======================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if(target){
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// =======================
// Form Validation & Success Feedback
// =======================
const contactForm = document.querySelector('.contact-form');

if(contactForm) {
  contactForm.addEventListener('submit', function(e){
    const name = this.name.value.trim();
    const email = this.email.value.trim();
    const message = this.message.value.trim();

    if(!name || !email || !message){
      e.preventDefault();
      alert("Please fill in all fields!");
      return false;
    }

    // Optional: show neon glow effect on submit
    this.querySelector('button').classList.add('glow');
    setTimeout(() => {
      this.querySelector('button').classList.remove('glow');
    }, 1000);
  });
}

// =======================
// Neon Button Hover Animation
// =======================
document.querySelectorAll('.btn, .dashboard-btn, .contact button').forEach(btn => {
  btn.addEventListener('mouseenter', () => {
    btn.style.boxShadow = '0 0 15px #00ffff, 0 0 30px #00ffff, 0 0 45px #00ffff';
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.boxShadow = 'none';
  });
});

// =======================
// Hero Section Neon Glow Animation
// =======================
const heroTitle = document.querySelector('.hero h2');
let glowIntensity = 0;
let increasing = true;

setInterval(() => {
  if(increasing){
    glowIntensity += 1;
    if(glowIntensity >= 20) increasing = false;
  } else {
    glowIntensity -= 1;
    if(glowIntensity <= 0) increasing = true;
  }
  heroTitle.style.textShadow = `0 0 ${glowIntensity}px #00ffff, 0 0 ${glowIntensity*2}px #00ffff`;
}, 100);

// =======================
// Optional: Dashboard Button Pulse
// =======================
const dashBtn = document.querySelector('.dashboard-btn');
setInterval(() => {
  dashBtn.style.transform = 'scale(1.05)';
  setTimeout(() => { dashBtn.style.transform = 'scale(1)'; }, 500);
}, 2000);
