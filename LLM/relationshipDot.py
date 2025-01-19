import json
from fuzzywuzzy import process
from store import save_to_json_file, get_latest_data
from entities import entities, priority_order, entity_scores 


# print("Entities:\n", entities)
# print("Priority Order:\n", priority_order)
# print("Entity Scores:\n", entity_scores)



# Scoring directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
# 0-3: Negative impact (not recommended).
# 4-6: Neutral impact (acceptable with adjustments).
# 7-10: Positive impact (highly recommended)

latest_data = get_latest_data()
if latest_data:
    
    room_types = latest_data.get('room_types', [])
    room_dimensions_list = latest_data.get('layout', {}).get('Dimension', [])
    # print("Room Types: \n", room_types)
    # print("Room Dimensions: \n", room_dimensions_list)
else:
    room_types = []
    room_dimensions_list = []
    print("No data available.")


def dot_product_score(room1_scores, room2_scores):
    return sum(a * b for a, b in zip(room1_scores, room2_scores))

def normalize_room_name(room_name):
    known_entities = list(entity_scores.keys())
    match, score = process.extractOne(
        room_name.replace("_1", "").replace("_2", "").replace("_3", "").lower(),
        known_entities,
        scorer=process.fuzz.token_sort_ratio
    )
    return match if score >= 80 else None  

def find_relationship_scores(entity_scores, room_types, priority_order):
    relationship_score = {}
    
    normalized_rooms = {}
    for room in room_types:
        normalized = normalize_room_name(room)
        if normalized:
            normalized_rooms[room] = normalized
        else:
            print(f"Warning: Could not normalize room name '{room}'. Skipping.")
    
    for i in range(len(room_types)):
        for j in range(i + 1, len(room_types)):
            room1 = room_types[i]
            room2 = room_types[j]
            
            normalized_room1 = normalized_rooms.get(room1)
            normalized_room2 = normalized_rooms.get(room2)
            
            if normalized_room1 and normalized_room2:
                scores1 = entity_scores.get(normalized_room1, [0]*8)
                scores2 = entity_scores.get(normalized_room2, [0]*8)
                
                score = dot_product_score(scores1, scores2)
                if score > 0:
                    
                    pair = tuple(sorted([room1, room2]))
                    relationship_score[pair] = score
    
    sorted_relationship_score = dict(sorted(relationship_score.items(), key=lambda item: item[1], reverse=True))
    return sorted_relationship_score

def create_placement_dict(room_types, room_dimensions_list, relationship_score):
    
    placement_dict = {"Dimensions": []}
    
    room_dimensions = {room['room_type']: room for room in room_dimensions_list}
    
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    
    for room in room_types:
        normalized_room = normalize_room_name(room)
        if normalized_room and room in room_dimensions:
            dimensions = room_dimensions[room]
            direction_scores = entity_scores.get(normalized_room, [0]*8)
            max_score = max(direction_scores)
            best_directions = [dir for score, dir in zip(direction_scores, directions) if score == max_score]
            
            placement_dict["Dimensions"].append({
                "room_type": room,
                "area": dimensions.get('area', 0),
                "width": dimensions.get('width', 0),
                "length": dimensions.get('length', 0),
                "min_aspect_ratio": dimensions.get('min_aspect_ratio', 1.0),
                "max_aspect_ratio": dimensions.get('max_aspect_ratio', 2.0),
                "direction_scores": direction_scores,
                "directions": best_directions,
                "neighbors": []   
            })
        else:
            print(f"Warning: No dimensions found for room '{room}' or unable to normalize.")
    
    for (room1, room2), score in relationship_score.items():
        
        room1_entry = next((item for item in placement_dict["Dimensions"] if item["room_type"] == room1), None)

        room2_entry = next((item for item in placement_dict["Dimensions"] if item["room_type"] == room2), None)
        
        if room1_entry and room2_entry:
            room1_entry["neighbors"].append({"room_type": room2, "relationship_score": score})

            room2_entry["neighbors"].append({"room_type": room1, "relationship_score": score})
    
    return placement_dict

relationship_score = find_relationship_scores(entity_scores, room_types, priority_order)

print("\nRelationship Scores (Sorted):\n" + "-"*50)
# for pair, score in relationship_score.items():
#     print(f"Room Pair: {pair} | Relationship Score: {score}")
print(relationship_score)

# final placement dictionary => isko import karke json mein save karna hai

placement_dict = create_placement_dict(room_types, room_dimensions_list, relationship_score)

print("\nPlacement Dictionary:\n" + "-"*50)
print(json.dumps(placement_dict,indent=2))
