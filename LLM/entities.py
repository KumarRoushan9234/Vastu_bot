import json
from store import save_to_json_file, get_latest_data

entities = [
    "kitchen", "bedroom", "bathroom", "pooja_room", "living_room", "dining_room",
    "study_room", "storeroom", "balcony", "utility_room", "guest_room",
    "home_office", "nursery", "laundry_room", "garage", "library", "media_room",
    "sunroom", "mudroom", "playroom", "pet_room", "reading_room",
    "storage_room", "garden_area", "balcony_garden",
]


entity_mapping = {
    "toilet": "washroom",
    "bathroom": "washroom",
    "restroom": "washroom",
    "wc": "washroom",
    "bedrooms": "bedroom",  
    "guestroom": "guest_room",
    "studyroom": "study_room",
    "storeroom": "storeroom",  
    "balconygarden": "balcony_garden",
    "garden": "garden_area",
    "office": "home_office",  
    # maybe other entity mapping
}

priority_order = [
    "pooja_room", "puja_room", "living_room", "dining_room", 
    "kitchen", "bedroom", "bathroom", "toilet", "study_room", "main_door", "garden", 
    "balcony", "guest_room", "home_office", "garage", "library", 
    "pet_room", "staircase", "septic_tank", "wall_clock", "water_tank"
]

# Scoring directions
# [N, NE, E, SE, S, SW, W, NW]
# 0-3: Negative impact (not recommended).
# 4-6: Neutral impact (acceptable with adjustments).
# 7-10: Positive impact (highly recommended)

entity_scores = {
    "pooja_room": [10, 0, 8, 0, 0, 0, 0, 0], 
    "puja_room": [10, 0, 8, 0, 0, 0, 0, 0],
    "kitchen": [0, 0, 8, 6, 0, 4, 3, 0],
    "bedroom": [3, 0, 0, 0, 7, 5, 0, 0],
    "toilet": [0, 0, 0, 3, 0, 0, 7, 0],       
    "bathroom": [0, 0, 0, 3, 0, 0, 7, 0],
    "washroom": [0, 0, 0, 3, 0, 0, 7, 0],
    "living_room": [7, 4, 9, 5, 6, 0, 0, 0],
    "drawing_room": [6, 5, 7, 4, 5, 0, 0, 0], 
    "dining_room": [8, 0, 6, 0, 0, 0, 6, 0],
    "study_room": [0, 0, 8, 6, 5, 3, 0, 0],
    "garden": [0, 0, 0, 0, 0, 8, 0, 0],
    "staircase": [0, 0, 0, 0, 6, 7, 0, 5],
    "main_door": [9, 0, 10, 0, 0, 0, 0, 0],
    "septic_tank": [0, 0, 0, 0, 0, 0, 9, 0],
    "wall_clock": [0, 0, 6, 0, 5, 0, 0, 0],
    "water_tank": [0, 0, 8, 0, 0, 0, 0, 0],
    "balcony": [0, 0, 5, 0, 0, 0, 6, 0],
    "guest_room": [0, 0, 5, 0, 0, 0, 0, 6],
    "home_office": [0, 0, 6, 0, 3, 4, 0, 0],
    "garage": [0, 0, 0, 5, 0, 0, 0, 0],
    "library": [0, 0, 6, 0, 5, 0, 0, 0],
    "pet_room": [0, 0, 5, 0, 0, 0, 0, 6],
}



# order or priority list
# 1. Main Door
# 2. Pooja Room/Puja Room
# 3. Living Room
# 4. Dining Room
# 5. Kitchen
# 6. Bedroom
# 7. Bathroom/Washroom/Toilet
# 8. Study Room
# 9. Garden
# 10. Balcony
# 11. Guest Room
# 12. Home Office
# 13. Garage
# 14. Library
# 15. Pet Room
# 16. Staircase
# 17. Septic Tank
# 18. Wall Clock
# 19. Water Tank



# fuzzywuzzy or python-Levenshtein(for faster matching)