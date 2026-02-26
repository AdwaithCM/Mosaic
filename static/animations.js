/**
 * PROJECT HYPER-MOSAIC: ANIMATION CONTROLLER
 * Handles Magnetic Buttons, Page Transitions, Greetings, and 3D Hardware Animations.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMagneticButtons();
    initGreeting();
    initPageTransitions();

    // NEW HARDWARE-ACCELERATED SYSTEMS
    initSystemBoot();
    initKineticCounters();
    initGlassTilt();

    initSpotlightGlow();
    initTerminalExecution();
});

/* --- 1. MAGNETIC BUTTONS --- */
function initMagneticButtons() {
    const magnets = document.querySelectorAll('.magnetic-btn');
    magnets.forEach((btn) => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            btn.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px)`;
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translate(0, 0)';
            btn.style.transition = 'transform 0.3s ease-out';
            setTimeout(() => { btn.style.transition = ''; }, 300);
        });
    });
}

/* --- 2. DYNAMIC GREETING --- */
function initGreeting() {
    const greetingEl = document.getElementById('dynamic-greeting');
    if (!greetingEl) return;

    const hour = new Date().getHours();
    let text = "Welcome Back, Executive";
    if (hour < 12) text = "Good Morning, Sir";
    else if (hour < 18) text = "Good Afternoon, Sir";
    else text = "Good Evening, Sir";

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

/* --- 3. PAGE TRANSITIONS (Hardware Accelerated) --- */
function initPageTransitions() {
    document.body.style.opacity = '0';
    requestAnimationFrame(() => {
        document.body.style.transition = 'opacity 0.3s ease-out';
        document.body.style.opacity = '1';
    });

    const links = document.querySelectorAll('a.nav-link');
    links.forEach(link => {
        link.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (!href || href.startsWith('#') || this.hasAttribute('data-bs-toggle') || this.target === '_blank') return;

            e.preventDefault();
            document.body.style.transition = 'opacity 0.15s ease-out';
            document.body.style.opacity = '0';
            setTimeout(() => { window.location.href = href; }, 150);
        });
    });
}

/* --- 4. SYSTEM BOOT CASCADE --- */
function initSystemBoot() {
    // Finds all your major UI blocks
    const elements = document.querySelectorAll('.glass-card, .terminal-window');

    elements.forEach((el, index) => {
        // Start pushed down and invisible
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.willChange = 'opacity, transform'; // Tells GPU to prep for movement

        // Stagger the entrance by 80ms per card
        setTimeout(() => {
            el.style.transition = 'opacity 0.6s ease-out, transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';

            // Clean up to free memory after animation
            setTimeout(() => {
                el.style.willChange = 'auto';
                el.style.transition = ''; // Clears transition so Hover Tilt works
            }, 600);
        }, 100 + (index * 80));
    });
}

/* --- 5. AMBIENT GLASS TILT (3D Micro-Interaction) --- */
function initGlassTilt() {
    const cards = document.querySelectorAll('.glass-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            // Subtle 2-degree max tilt
            const rotateX = ((y - centerY) / centerY) * -2;
            const rotateY = ((x - centerX) / centerX) * 2;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });

        card.addEventListener('mouseleave', () => {
            // Smooth snap back to flat
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg)`;
            card.style.transition = 'transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1)';
            setTimeout(() => { card.style.transition = ''; }, 500);
        });
    });
}


/* --- 6. KINETIC DATA COUNTERS (Smart Format Edition) --- */
function initKineticCounters() {
    const counters = document.querySelectorAll('.kinetic-counter');

    counters.forEach(counter => {
        const targetText = counter.innerText.trim();

        // 1. Extract the pure math number
        const target = parseFloat(targetText.replace(/[^0-9.]/g, ''));
        if (isNaN(target)) return;

        // 2. Auto-Detect Formatting (Prefixes, Suffixes, and Decimals)
        const prefixMatch = targetText.match(/^[^0-9]+/); // Catches ₹, $, etc.
        const prefix = prefixMatch ? prefixMatch[0] : '';

        const suffixMatch = targetText.match(/[^0-9.]+$/); // Catches %, etc.
        const suffix = suffixMatch ? suffixMatch[0] : '';

        // Count how many decimal places exist in the original text (e.g., "12.5" = 1)
        const decimals = targetText.includes('.') ? targetText.split('.')[1].replace(/[^0-9]/g, '').length : 0;

        const duration = 1200;
        const startTime = performance.now();

        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentVal = target * easeOut;

            // 3. Format with exact decimals and standard Indian commas (e.g., 1,00,000)
            const formattedNum = currentVal.toLocaleString('en-IN', {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals
            });

            if (progress < 1) {
                // Spin with symbols and decimals intact
                counter.innerText = prefix + formattedNum + suffix;
                requestAnimationFrame(updateCounter);
            } else {
                // Final frame: Re-calculate the target with proper commas so it doesn't lose them!
                const finalNum = target.toLocaleString('en-IN', {
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals
                });
                counter.innerText = prefix + finalNum + suffix;
            }
        };
        requestAnimationFrame(updateCounter);
    });
}

/* --- 7. VERCEL SPOTLIGHT GLOW (Zero-Lag Cursor Tracking) --- */
function initSpotlightGlow() {
    const cards = document.querySelectorAll('.glass-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            // Calculate exact mouse position inside the specific card
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Pipe the coordinates directly to CSS in real-time
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
}

/* --- 8. TERMINAL EXECUTION SEQUENCE --- */
function initTerminalExecution() {
    // Find every individual action item inside the terminal
    const terminalItems = document.querySelectorAll('.terminal-window li');
    if (terminalItems.length === 0) return;

    // 1. Hide them and push them slightly left on load
    terminalItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(-15px)';
        item.style.willChange = 'opacity, transform';
    });

    // 2. Wait 800ms for the main Dashboard "System Boot" to finish first
    setTimeout(() => {
        terminalItems.forEach((item, index) => {
            // 3. Stagger the typing effect by 250ms per line
            setTimeout(() => {
                item.style.transition = 'opacity 0.4s ease-out, transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1)';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';

                // Cleanup memory
                setTimeout(() => { item.style.willChange = 'auto'; }, 400);
            }, index * 250);
        });
    }, 800);
}