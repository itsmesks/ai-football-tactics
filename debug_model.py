import joblib
import pandas as pd

try:
    print("Loading models...")
    model = joblib.load("model.pkl")
    encoders = joblib.load("encoders.pkl")
    output_encoder = joblib.load("output_encoder.pkl")
    print("Models loaded successfully.")

    # Input validation (mocking the form data)
    input_data_list = [
        "4-3-3", # opponent_formation
        60,      # opponent_possession
        85,      # pass_accuracy
        5,       # shots_on_target
        "High"   # pressing_style
    ]
    
    encoded_input = []
    columns = [
        "opponent_formation",
        "opponent_possession",
        "pass_accuracy",
        "shots_on_target",
        "pressing_style"
    ]

    print("Encoding input...")
    for i, col in enumerate(columns):
        if col in encoders:
            val = encoders[col].transform([input_data_list[i]])[0]
            print(f"Encoded {col}: {val}")
            encoded_input.append(val)
        else:
            print(f"Passed {col}: {input_data_list[i]}")
            encoded_input.append(input_data_list[i])

    print("Encoded Input Vector:", encoded_input)
    
    print("Predicting...")
    prediction_val = model.predict([encoded_input])
    print("Raw Prediction:", prediction_val)
    
    result = output_encoder.inverse_transform(prediction_val)[0]
    print("Decoded Result:", result)
    
except Exception as e:
    print("FAILED with error:", e)
