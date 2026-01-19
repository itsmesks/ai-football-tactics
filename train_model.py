import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
data = pd.read_csv("dataset.csv")

# Input features
X = data[[
    "opponent_formation",
    "opponent_possession",
    "pass_accuracy",
    "shots_on_target",
    "pressing_style"
]]

# Output labels
y = data["recommended_formation"]

# Encode categorical data
encoders = {}

for column in X.columns:
    if X[column].dtype == "object":
        le = LabelEncoder()
        X[column] = le.fit_transform(X[column])
        encoders[column] = le

# Encode output
output_encoder = LabelEncoder()
y = output_encoder.fit_transform(y)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model and encoders
joblib.dump(model, "model.pkl")
joblib.dump(encoders, "encoders.pkl")
joblib.dump(output_encoder, "output_encoder.pkl")

print("✅ Model training completed and saved successfully!")
