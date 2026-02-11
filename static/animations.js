/**
 * PROJECT HYPER-MOSAIC: ANIMATION CONTROLLER
 * Handles Magnetic Buttons, Page Transitions, and Dynamic Greetings.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMagneticButtons();
    initGreeting();
    initPageTransitions();
});

/* --- 1. MAGNETIC BUTTONS --- */
function initMagneticButtons() {
    const magnets = document.querySelectorAll('.magnetic-btn');

    magnets.forEach((btn) => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            // intensity factor (lower = stronger pull)
            btn.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translate(0, 0)';
            // Add a transition for the snap-back
            btn.style.transition = 'transform 0.3s ease-out';
            setTimeout(() => {
                btn.style.transition = ''; // Remove transition so mousemove is instant
            }, 300);
        });
    });
}

/* --- 2. DYNAMIC GREETING --- */
function initGreeting() {
    const greetingEl = document.getElementById('dynamic-greeting');
    if (!greetingEl) return;

    const hour = new Date().getHours();
    let text = "Welcome Back, Executive";

    if (hour < 12) text = "Good Morning, Niranjan";
    else if (hour < 18) text = "Good Afternoon, Niranjan";
    else text = "Good Evening, Niranjan";

    // Typewriter Effect
    let i = 0;
    greetingEl.innerHTML = "";
    const typeWriter = () => {
        if (i < text.length) {
            greetingEl.innerHTML += text.charAt(i);
            i++;
            setTimeout(typeWriter, 50);
        }
    };
    typeWriter();
}

/* --- 3. PAGE TRANSITIONS --- */
function initPageTransitions() {
    // Add fade-in class to body on load
    document.body.classList.add('fade-in');

    const links = document.querySelectorAll('a.nav-link');
    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const href = this.getAttribute('href');

            // Fade out
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.3s ease';

            setTimeout(() => {
                window.location.href = href;
            }, 300);
        });
    });
}
