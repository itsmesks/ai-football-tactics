import joblib
import pandas as pd
import os

class TacticalEngine:
    def __init__(self, model_path="model.pkl", encoders_path="encoders.pkl", output_encoder_path="output_encoder.pkl"):
        self.model = None
        self.encoders = None
        self.output_encoder = None
        self.load_artifacts(model_path, encoders_path, output_encoder_path)

    def load_artifacts(self, model_path, encoders_path, output_encoder_path):
        """Load ML artifacts safely."""
        try:
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
            if os.path.exists(encoders_path):
                self.encoders = joblib.load(encoders_path)
            if os.path.exists(output_encoder_path):
                self.output_encoder = joblib.load(output_encoder_path)
        except Exception as e:
            print(f"Warning: Could not load ML artifacts: {e}. Falling back to rule-based logic only.")

    def predict(self, input_data):
        """
        Main prediction method using Hybrid Intelligence (Rules + ML).
        
        input_data: dict containing:
            - opponent_formation (str)
            - opponent_possession (int)
            - pass_accuracy (int)
            - shots_on_target (int)
            - pressing_style (str)
        """
        
        # 1. Rule-Based Analysis (The "Expert System" Layer)
        # We start with football logic to guide or override the ML model.
        
        formation = input_data.get("opponent_formation")
        possession = int(input_data.get("opponent_possession", 50))
        pressing = input_data.get("pressing_style", "Medium")
        
        recommended_formation = None
        explanation = []

        # High-level strategic rules
        if possession > 65:
            # Opponent dominates ball -> We need a solid block and counter-attack.
            # 5-4-1 or 4-4-2 Low Block are good.
            explanation.append("Opponent dominates possession (>65%). A compact defensive structure is required to absorb pressure and counter-attack into space.")
            if formation in ["4-3-3", "3-4-3"]:
                 # Against wide attackers, 5 at the back helps.
                 recommended_formation = "5-4-1"
                 explanation.append("A 5-4-1 formation provides defensive width and prevents overload on the wings against their 3-forward line.")
            else:
                 recommended_formation = "4-4-2"
                 explanation.append("A structured 4-4-2 low block allows for two banks of four to deny space between lines.")
        
        elif pressing == "High":
            # Opponent presses high -> We need stability or long ball outlets.
            explanation.append("Opponent employs a High Press. Risks of turnover in build-up are high.")
            if possession < 40:
                # We don't have ball, they press -> Bypass midfield.
                recommended_formation = "4-4-2"
                explanation.append("Use a 4-4-2 to provide two direct outlets (strikers) and bypass their midfield press.")
            else:
                # We want to play -> We need numerical superiority or triangles.
                recommended_formation = "4-3-3"
                explanation.append("A 4-3-3 offers triangles for passing options to play through the high press.")

        elif formation == "3-5-2" or formation == "5-3-2":
            # Opponent has strong center, potentially weak wings if wingbacks are pinned.
            explanation.append(f"Opponent is playing {formation}, which is strong centrally.")
            recommended_formation = "4-3-3"
            explanation.append("A 4-3-3 allows us to exploit the spaces behind their wingbacks with our wingers.")

        elif formation == "4-4-2":
            # Standard flat 4-4-2. We can overload midfield.
            recommended_formation = "4-2-3-1"
            explanation.append("Against a flat 4-4-2, a 4-2-3-1 gives us a 3v2 numerical advantage in central midfield.")

        # 2. ML-Based Refinement (The "Data" Layer)
        # If rules didn't strongly dictate a specific formation, or to validate, we use ML.
        # For this implementation, we will use ML if no strong rule fired, or to augment the explanation.
        
        if recommended_formation is None and self.model is not None:
            try:
                # Prepare input vector
                # Note: This must match the training order strictly.
                # ["opponent_formation", "opponent_possession", "pass_accuracy", "shots_on_target", "pressing_style"]
                
                features = [
                    input_data["opponent_formation"],
                    int(input_data["opponent_possession"]),
                    int(input_data["pass_accuracy"]),
                    int(input_data["shots_on_target"]),
                    input_data["pressing_style"]
                ]
                
                # Encode
                encoded_features = []
                columns = ["opponent_formation", "opponent_possession", "pass_accuracy", "shots_on_target", "pressing_style"]
                
                for i, col in enumerate(columns):
                    if col in self.encoders:
                        val = self.encoders[col].transform([features[i]])[0]
                        encoded_features.append(val)
                    else:
                        encoded_features.append(features[i])
                
                # Predict
                pred = self.model.predict([encoded_features])
                ml_recommendation = self.output_encoder.inverse_transform(pred)[0]
                
                if recommended_formation is None:
                    recommended_formation = ml_recommendation
                    explanation.append(f"Statistical analysis of similar match situations suggests {ml_recommendation} is the optimal counter.")
                    
            except Exception as e:
                print(f"ML Prediction failed: {e}")
                # Fallback default
                if recommended_formation is None:
                    recommended_formation = "4-2-3-1"
                    explanation.append("Recommended largely due to its balanced nature and flexibility.")

        # Final Fallback
        if recommended_formation is None:
            recommended_formation = "4-2-3-1"
            explanation.append("Selected as a balanced starting point to assess opponent weaknesses.")

        # Extended Tactical Directives
        # Determine specific instructions based on game state
        
        # 1. Attacking Style
        attack_style = "Balanced"
        if possession > 60:
            attack_style = "Counter Attack" # If they have ball, we counter
        elif possession < 40:
            attack_style = "Possession Control" # If we have ball (opponent low poss), we keep it
        elif "4-4-2" in formation or "4-3-1-2" in formation:
             attack_style = "Wing Play" # Stretch them
        
        # 2. Defensive Style
        defense_style = "Mid Block"
        shots = int(input_data.get("shots_on_target", 5))
        if shots > 8:
            defense_style = "Low Block" # They are dangerous, sit back
        elif pressing == "High":
            defense_style = "High Press" # Fight fire with fire or breaking lines? Let's say High Press to disrupt
        
        # 3. Tempo
        tempo = "Standard"
        pass_acc = int(input_data.get("pass_accuracy", 80))
        if pass_acc > 88:
             tempo = "Slow & Patient" # They pass well, we must be patient
        elif attack_style == "Counter Attack":
             tempo = "Fast / Direct"

        # 4. Key Instruction
        key_instruction = "Maintain formation discipline."
        if attack_style == "Wing Play":
            key_instruction = "Overload the flanks and cross early."
        elif defense_style == "Low Block":
            key_instruction = "Stay compact and force shots from distance."
        elif pressing == "High":
            key_instruction = "Bypass midfield with long balls to strikers."

         # Player Archetype Logic (Existing)
        # Select a "Key Player Style" based on the tactical context
        key_player = "neymar" # default
        player_desc = "Creative genius needed to break down structured defenses."

        if possession > 60:
            # High possession match -> Need a playmaker/controller
            key_player = "messi"
            player_desc = "Orchestrator needed to control tempo and exploit small spaces."
        elif possession < 45 or pressing == "High":
             # Counter attack or break press -> Need power and directness
             key_player = "ronaldo"
             player_desc = "Clinical finisher needed for fast transitions and counter-attacks."
        else:
            # Balanced/Chaos -> Need flair
            key_player = "neymar"
            player_desc = "Creative playmaker needed to unlock defense with individual brilliance."

        # Normalize outputs to fit "Production" JSON standard
        full_explanation = " ".join(explanation)
        
        return {
            "recommended_formation": recommended_formation,
            "tactical_explanation": full_explanation,
            "tactics": {
                "attacking_style": attack_style,
                "defensive_style": defense_style,
                "tempo": tempo,
                "key_instruction": key_instruction
            },
            "key_player_archetype": {
                "name": key_player,
                "description": player_desc
            }
        }
