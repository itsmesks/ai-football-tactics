from flask import Flask, render_template, request
import joblib

app = Flask(__name__)

# Load model and encoders
model = joblib.load("model.pkl")
encoders = joblib.load("encoders.pkl")
output_encoder = joblib.load("output_encoder.pkl")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    know = request.form

    input_data = [
        know["opponent_formation"],
        int(know["opponent_possession"]),
        int(know["pass_accuracy"]),
        int(know["shots_on_target"]),
        know["pressing_style"]
    ]

    encoded_input = []
    columns = [
        "opponent_formation",
        "opponent_possession",
        "pass_accuracy",
        "shots_on_target",
        "pressing_style"
    ]

    for i, col in enumerate(columns):
        if col in encoders:
            encoded_input.append(encoders[col].transform([input_data[i]])[0])
        else:
            encoded_input.append(input_data[i])

    prediction = model.predict([encoded_input])
    result = output_encoder.inverse_transform(prediction)[0]

    explanation = ""

    pressing = know["pressing_style"]
    possession = int(know["opponent_possession"])

    if result == "4-3-3":
        explanation = "Provides width and counters balanced teams."
    elif result == "4-2-3-1":
        explanation = "Improves midfield stability against high press."
    elif result == "3-5-2":
        explanation = "Strengthens midfield dominance."
    else:
        explanation = "Balanced formation for flexible play."

    if pressing == "High":
        explanation += " Quick passing is advised to escape high press."
    elif pressing == "Low":
        explanation += " Possession-based play will be effective."

    if possession > 55:
        explanation += " Opponent dominates possession, so structured defense is needed."
    else:
        explanation += " Counter-attacking opportunities are available."

    return render_template(
        "index.html",
        prediction=result,
        explanation=explanation
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

