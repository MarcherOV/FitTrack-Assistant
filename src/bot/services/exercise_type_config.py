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

INFO_TEXT_ABOUT_SET ={
    1: "Set {set_number}: {set_weight} kg x {set_reps}",
    2: "Set {set_number}: {set_distance} km for {set_processing_time}; Cal: {set_calories_burned}",
    3: "Set {set_number}: {set_reps} with {set_weight} kg",
    4: "Set {set_number}: {processing_time} with {set_weight} kg"
}