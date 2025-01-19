import json
from fuzzywuzzy import process  
from store import save_to_json_file, get_latest_data
from entities import entities, priority_order, entity_scores

# Directions: [N, NE, E, SE, S, SW, W, NW]
# 0-3: Negative impact (not recommended).
# 4-6: Neutral impact (acceptable with adjustments).
# 7-10: Positive impact (highly recommended)

latest_data = get_latest_data()
if latest_data:
    room_types = latest_data.get('room_types', [])
    print("Room Types : ", room_types)
else:
    room_types = []
    print("No data available.")

def compatibility_score(room1_scores, room2_scores):
    score = 0
    for i in range(len(room1_scores)):
        if room1_scores[i] >= 3 and room2_scores[i] >= 3:  
            score += room1_scores[i] + room2_scores[i]
    return score

def normalize_room_name(room_name):
    
    known_entities = list(entity_scores.keys())
    
    match, score = process.extractOne(room_name.replace("_1", "").replace("_2", "").replace("_3", ""), known_entities)
    return match if score >= 80 else None  

def find_best_room_pairs(entity_scores, room_types):
    best_pairs = []
    for i in range(len(room_types)):
        for j in range(i + 1, len(room_types)):
            room1 = room_types[i]
            room2 = room_types[j]

            normalized_room1 = normalize_room_name(room1)
            normalized_room2 = normalize_room_name(room2)

            if normalized_room1 and normalized_room2:
                scores1 = entity_scores.get(normalized_room1, [0]*8)
                scores2 = entity_scores.get(normalized_room2, [0]*8)

                score = compatibility_score(scores1, scores2)
                if score > 0:  
                    best_pairs.append((room1, room2, score))
    
    best_pairs.sort(key=lambda x: x[2], reverse=True)
    return best_pairs

best_room_pairs = find_best_room_pairs(entity_scores, room_types)

print("\nBest Room Pairs and Their Compatibility Scores:\n" + "-"*50)
if best_room_pairs:
    for pair in best_room_pairs:
        print(f"Room Pair: {pair[0]} and {pair[1]} | Compatibility Score: {pair[2]}")
else:
    print("No compatible room pairs found.")
