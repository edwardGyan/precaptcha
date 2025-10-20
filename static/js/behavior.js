let behaviorData = {
    mouse: [],
    typing: [],
    idleTimes: [],
    lastActivity: Date.now(),
    lastMouse: null,
    lastKeyTime: null
};

// --- Record Idle ---
function recordIdle() {
    const now = Date.now();
    const idle = now - behaviorData.lastActivity;

    const idleType = idle > 2000 ? "long" : idle > 500 ? "short" : "very_short";
    behaviorData.idleTimes.push({
        duration: idle,
        type: idleType,
        t: now
    });

    behaviorData.lastActivity = now;
}

// --- Mouse Movement ---
document.addEventListener("mousemove", e => {
    recordIdle();

    const now = Date.now();
    const prev = behaviorData.lastMouse;
    let speed = null;

    if (prev) {
        const dx = e.clientX - prev.x;
        const dy = e.clientY - prev.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const dt = now - prev.t;
        if (dt > 0) speed = dist / dt; // px per ms
    }

    const current = { x: e.clientX, y: e.clientY, t: now, speed };
    behaviorData.mouse.push(current);
    behaviorData.lastMouse = current;
});

// --- Typing ---
document.addEventListener("keydown", e => {
    recordIdle();

    const now = Date.now();
    let interval = null;

    if (behaviorData.lastKeyTime) {
        interval = now - behaviorData.lastKeyTime;
    }

    behaviorData.typing.push({
        key: e.key,
        t: now,
        interval
    });

    behaviorData.lastKeyTime = now;
});

// --- Submit Form ---
const form = document.getElementById("registerForm");
if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            behavior: behaviorData,
            timestamp: new Date().toISOString()
        };

        try {
            const res = await fetch("/verify_behavior", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const result = await res.json();

            const resultDiv = document.getElementById("result");
            resultDiv.innerHTML = `
                <div class="alert alert-${result.verified ? 'success' : 'danger'} mt-3" role="alert">
                    <strong>${result.verified ? 'Human Verified ✅' : 'Verification Failed ❌'}</strong><br>
                    <code>Score: ${result.score}</code>
                </div>
                <pre class="bg-light p-2 text-start rounded" style="font-size: 0.85rem; overflow-x: auto;">
${JSON.stringify(result.debug_data, null, 2)}
                </pre>
            `;
        } catch (error) {
            console.error("Verification error:", error);
            document.getElementById("result").innerHTML =
                `<p class='text-danger'>Error verifying behavior.</p>`;
        }
    });
}
