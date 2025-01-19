import json
from fuzzywuzzy import process  
from store import save_to_json_file, get_latest_data
from entities import entities, priority_order, entity_scores

# Scoring directions
# [N, NE, E, SE, S, SW, W, NW]
# 0-3: Negative impact (not recommended).
# 4-6: Neutral impact (acceptable with adjustments).
# 7-10: Positive impact (highly recommended)


latest_data = get_latest_data()
if latest_data:
    room_types = latest_data.get('room_types', [])
    room_dimensions = latest_data.get('layout', {})
    print("Room Types: \n", room_types)
    print("Room Dimensions: \n", room_dimensions)
else:
    room_types = []
    room_dimensions = {}
    print("No data available.")

def compatibility_score(room1_scores, room2_scores):
    score = 0
    for i in range(len(room1_scores)):
        if room1_scores[i] >= 3 and room2_scores[i] >= 3:  
            score += room1_scores[i] + room2_scores[i]
    return score

def normalize_room_name(room_name):
    known_entities = list(entity_scores.keys())
    
    base_room = room_name.split('_')[0]
    
    match, score = process.extractOne(base_room, known_entities)
    return match if score >= 80 else None  

def get_priority_level(room_name):
    
    try:
        return priority_order.index(room_name)
    except ValueError:
        return float('inf')  

def find_best_room_pairs(entity_scores, room_types, priority_order):
    
    best_pairs = []
    
    priority_index = {room: index for index, room in enumerate(priority_order)}
    
    sorted_room_types = sorted(room_types, key=lambda x: priority_index.get(normalize_room_name(x), float('inf')))
    
    for i in range(len(sorted_room_types)):
        room1 = sorted_room_types[i]
        normalized_room1 = normalize_room_name(room1)
        if not normalized_room1:
            continue
        scores1 = entity_scores.get(normalized_room1, [0]*8)
        
        for j in range(i + 1, len(sorted_room_types)):
            room2 = sorted_room_types[j]
            normalized_room2 = normalize_room_name(room2)
            if not normalized_room2:
                continue
            scores2 = entity_scores.get(normalized_room2, [0]*8)
            
            score = compatibility_score(scores1, scores2)
            if score > 0:
                priority_sum = get_priority_level(normalized_room1) + get_priority_level(normalized_room2)
                best_pairs.append((room1, room2, score, priority_sum))
    
    unique_best_pairs = []
    seen = set()
    for pair in best_pairs:
        sorted_pair = tuple(sorted([pair[0], pair[1]]))
        if sorted_pair not in seen:
            unique_best_pairs.append(pair)
            seen.add(sorted_pair)
    
    unique_best_pairs.sort(key=lambda x: (-x[2], x[3]))
    return unique_best_pairs

best_room_pairs = find_best_room_pairs(entity_scores, room_types, priority_order)

print("\nBest Room Pairs and Their Compatibility Scores:\n" + "-"*50)
if best_room_pairs:
    for pair in best_room_pairs:
        print(f"Room Pair: {pair[0]} and {pair[1]} | Compatibility Score: {pair[2]} | Priority Sum: {pair[3]}")
else:
    print("No compatible room pairs found.")

placement_dict = {"Dimensions": []}

for room in room_types:
    normalized_room = normalize_room_name(room)
    if normalized_room:
       
        if room in room_dimensions:
            dimensions = room_dimensions[room]
        elif normalized_room in room_dimensions:
            dimensions = room_dimensions[normalized_room]
        else:
            dimensions = {}
        placement_dict["Dimensions"].append({
            "room_type": room,
            "area": dimensions.get('area', 0),
            "width": dimensions.get('width', 0),
            "length": dimensions.get('length', 0),
            "min_aspect_ratio": dimensions.get('min_aspect_ratio', 1.0),
            "max_aspect_ratio": dimensions.get('max_aspect_ratio', 2.0),
            "direction_scores": entity_scores.get(normalized_room, [0]*8),
            "directions": [],  
            # based on highest score direction
            "neighbors": []    
            # based on best_room_pairs
        })

directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

for room in placement_dict["Dimensions"]:
    direction_scores = room["direction_scores"]
    max_score = max(direction_scores)
    if max_score > 0:
        best_directions = [dir for score, dir in zip(direction_scores, directions) if score == max_score]
        room["directions"] = best_directions

for pair in best_room_pairs:
    room1, room2, score, priority_sum = pair
    
    room1_entry = next((item for item in placement_dict["Dimensions"] if item["room_type"] == room1), None)

    room2_entry = next((item for item in placement_dict["Dimensions"] if item["room_type"] == room2), None)
    
    if room1_entry and room2_entry:
        room1_entry["neighbors"].append({"room_type": room2, "compatibility_score": score})

        room2_entry["neighbors"].append({"room_type": room1, "compatibility_score": score})

print("\nPlacement Dictionary:\n" + "-"*50)
print(json.dumps(placement_dict, indent=4))
