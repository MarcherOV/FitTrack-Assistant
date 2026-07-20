EXERCISE_TYPE_CONFIG = {
    1: ["weight", "repetitions"],                          # Strength
    2: ["distance", "processing_time", "calories_burned"], # Cardio
    3: ["repetitions", "weight"],                          # Bodyweight
    4: ["processing_time", "weight"]                       # Timed
}

FIELD_PROMPTS = {
    "weight": "⚖️ Enter your weight (kg):",
    "repetitions": "🔄 Enter the number of repetitions:",
    "distance": "🏃 Enter the distance covered (km/m):",
    "processing_time": "⏱ Enter the execution time (in seconds):",
    "calories_burned": "🔥 Enter the number of calories burned:"
}