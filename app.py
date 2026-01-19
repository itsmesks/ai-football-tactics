from flask import Flask, render_template, request, jsonify, url_for
from core.decision_engine import TacticalEngine

app = Flask(__name__)

# Initialize Decision Engine
# Ensure specific artifacts are present or handle gracefully in the engine
engine = TacticalEngine()

@app.route("/")
def home():
    """
    Serves the Presentation Layer (Frontend).
    Backend logic for UI rendering is minimal.
    """
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """
    API Endpoint: POST /predict
    Accepts JSON input for match parameters.
    Returns JSON output with tactical recommendations.
    """
    try:
        # 1. Input Parsing & Validation
        # Support both JSON payload and Form Data (for flexibility, though JSON is preferred)
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()

        # Strict Validation
        required_fields = ["opponent_formation", "opponent_possession", "pass_accuracy", "shots_on_target", "pressing_style"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Type conversion safety
        try:
            clean_data = {
                "opponent_formation": str(data["opponent_formation"]),
                "opponent_possession": int(data["opponent_possession"]),
                "pass_accuracy": int(data["pass_accuracy"]),
                "shots_on_target": int(data["shots_on_target"]),
                "pressing_style": str(data["pressing_style"])
            }
        except ValueError:
             return jsonify({"error": "Invalid data types provided. Numeric values required for stats."}), 400

        # 2. Decision Engine Invocation
        result = engine.predict(clean_data)

        # 3. Response Formatting
        # Construct the "Production-Quality" response
        formation_slug = result["recommended_formation"]
        image_url = url_for('static', filename=f'images/{formation_slug}.png')
        
        player_slug = result["key_player_archetype"]["name"]
        player_image_url = url_for('static', filename=f'images/players/{player_slug}.png')

        response_payload = {
            "recommended_formation": result["recommended_formation"],
            "tactical_explanation": result["tactical_explanation"],
            "detailed_tactics": result["tactics"],
            "key_player": result["key_player_archetype"],
            "visual_assets": {
                "formation_image": image_url,
                "player_image": player_image_url
            }
        }

        return jsonify(response_payload), 200

    except Exception as e:
        # No silent failures
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "Internal Server Error during tactical analysis."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)

