document.getElementById('tacticForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const form = this;
    const submitBtn = form.querySelector('button[type="submit"]');
    const loadingOverlay = document.getElementById('loading-overlay');

    // Show Loading Overlay and reset button text
    loadingOverlay.style.display = 'flex';
    submitBtn.disabled = true;

    const formData = new FormData(this);
    const resultSection = document.getElementById('result-section');
    const resultFormation = document.getElementById('result-formation');
    const resultExplanation = document.getElementById('result-explanation');
    const resultImage = document.getElementById('result-image');

    const resultPlayerName = document.getElementById('player-name');
    const resultPlayerDesc = document.getElementById('player-desc');
    const resultPlayerImage = document.getElementById('player-image');

    // Reset result view
    resultSection.classList.add('collapsed');

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            // Update Content
            resultFormation.textContent = data.recommended_formation;
            resultExplanation.textContent = data.tactical_explanation;
            resultImage.src = data.visual_assets.formation_image;

            // Detailed Tactics
            document.getElementById('tactic-attack').textContent = data.detailed_tactics.attacking_style;
            document.getElementById('tactic-defense').textContent = data.detailed_tactics.defensive_style;
            document.getElementById('tactic-tempo').textContent = data.detailed_tactics.tempo;
            document.getElementById('tactic-instruction').textContent = data.detailed_tactics.key_instruction;

            // Player data
            resultPlayerName.textContent = data.key_player.name.toUpperCase();
            resultPlayerDesc.textContent = data.key_player.description;
            resultPlayerImage.src = data.visual_assets.player_image;

            // Wait for image to load before showing
            resultImage.onload = () => {
                resultSection.classList.remove('collapsed');
                resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
            };

            // Fallback
            if (resultImage.complete) {
                resultSection.classList.remove('collapsed');
                resultSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }

        } else {
            alert("Error: " + (data.error || "Unknown error occurred"));
        }
    } catch (err) {
        console.error('Error:', err);
        alert("Failed to connect to server.");
    } finally {
        loadingOverlay.style.display = 'none';
        submitBtn.disabled = false;
    }
});

// Interactive Card Selection (Optional enhancement to standard radio behavior)
document.querySelectorAll('.formation-card input').forEach(input => {
    input.addEventListener('change', function () {
        document.querySelectorAll('.formation-card').forEach(card => card.classList.remove('active'));
        if (this.checked) {
            this.parentElement.classList.add('active');
        }
    });
});
// Initialize active state
document.querySelector('.formation-card input:checked').parentElement.classList.add('active');
