// --- CANVAS ENGINE ---
const canvas = document.getElementById('skyCanvas');
const ctx = canvas.getContext('2d');
let stars = [], shootingStars = [];

function setup() {
    canvas.width = window.innerWidth; canvas.height = window.innerHeight;
    stars = [];
    for (let i = 0; i < 200; i++) {
        stars.push({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, size: Math.random() * 1.5, opacity: Math.random() });
    }
}

function createShootingStar() {
    shootingStars.push({ x: Math.random() * canvas.width, y: 0, len: Math.random() * 100 + 50, speed: Math.random() * 12 + 5, opacity: 1 });
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    stars.forEach(s => {
        ctx.fillStyle = `rgba(255, 255, 255, ${s.opacity})`;
        ctx.beginPath(); ctx.arc(s.x, s.y, s.size, 0, Math.PI*2); ctx.fill();
    });
    shootingStars.forEach((ss, i) => {
        ss.x -= ss.speed; ss.y += ss.speed * 0.7; ss.opacity -= 0.015;
        if (ss.opacity > 0) {
            ctx.strokeStyle = `rgba(167, 139, 250, ${ss.opacity})`;
            ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(ss.x, ss.y);
            ctx.lineTo(ss.x + ss.len, ss.y - ss.len*0.7); ctx.stroke();
        } else shootingStars.splice(i, 1);
    });
    if (Math.random() < 0.02) createShootingStar();
    requestAnimationFrame(draw);
}

// --- DATA ENGINE ---
async function fetchReleases() {
    const container = document.getElementById('dynamic-builds');
    try {
        const response = await fetch('versions.json');
        if (!response.ok) throw new Error('No se pudo cargar el JSON');
        const data = await response.json();

        container.innerHTML = data.map(item => `
            <div class="card">
                <div>
                    <span style="color: ${item.type === 'stable' ? '#10b981' : 'var(--soft-violet)'}; font-size: 0.6rem; font-weight: 900; letter-spacing: 1px;">
                        ${item.type.toUpperCase()}
                    </span>
                    <h3>${item.title}</h3>
                    <span class="version">${item.version}</span>
                    <ul class="specs">
                        ${item.changelog.map(log => `<li>${log}</li>`).join('')}
                    </ul>
                </div>
                <a href="${item.url}" class="dl-btn ${item.type === 'beta' ? 'dl-btn-beta' : ''}">
                    ${item.type === 'stable' ? 'Download Stable' : 'Get Beta Build'}
                </a>
            </div>
        `).join('');
    } catch (err) {
        console.error("Error:", err);
        container.innerHTML = "<p>Error al sincronizar con el servidor de versiones.</p>";
    }
}

// --- INITIALIZE ---
window.addEventListener('resize', setup);
window.addEventListener('DOMContentLoaded', () => {
    setup(); draw(); fetchReleases();
});
