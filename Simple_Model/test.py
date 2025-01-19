import re
from difflib import get_close_matches

valid_rooms = {
    'bedroom': 'bedroom',
    'toilet': 'toilet',
    'bathroom': 'bathroom',
    'kitchen': 'kitchen',
    'drawing_room': 'drawing room',
    'pooja_room': 'pooja room',
    'common_balcony': 'common balcony',
    'guest_room': 'guest room',
    'garage': 'garage',
    'living_room': 'living room',
    'study_room': 'study room',
    'courtyard': 'courtyard',
    'children_room': 'children room'
}

def extract_pattern(text):
    room_dict = {}
    pattern = r'(\d+)\s+([a-zA-Z\s]+)'
    matches = re.findall(pattern, text)

    for number, room_type in matches:
        room_type_cleaned = room_type.strip().lower().replace(" ", "_")
        
        standardized_room_type = get_close_matches(room_type_cleaned, valid_rooms.keys(), n=1, cutoff=0.6)
        
        if standardized_room_type:
            key = valid_rooms[standardized_room_type[0]]
            if key in room_dict:
                room_dict[key] += int(number)
            else:
                room_dict[key] = int(number)
    
    return room_dict

def calculate_dimensions(total_sq_ft, room_dict):
    allocation = {
        'courtyard': 0.10,
        'bedroom': 0.15,
        'bedroom_2': 0.12,
        'toilet': 0.07,
        'living_room': 0.18,
        'latrine': 0.05,          
        'store': 0.07,            
        'kitchen': 0.10,          
        'dining_room': 0.12,   
        'staircase': 0.05,    
        'study_room': 0.08,  
        'verandah': 0.07,       
        'garage': 0.10,     
        'drawing_room': 0.15, 
        'children_room': 0.10, 
        'guest_room': 0.10, 
        'treasury': 0.05,    
        'pooja_room': 0.05,
        'corridor': 0.10
    }
    
    total_allocation = sum(allocation.values())
    normalized_allocation = {room: value / total_allocation for room, value in allocation.items()}
    
    dimension1 = {}
    remaining_area = total_sq_ft
    
    for room, count in room_dict.items():
        if room in normalized_allocation:
            area_per_room = normalized_allocation[room] * total_sq_ft / count
            remaining_area -= area_per_room * count
            
            if room == 'bedroom':
                for i in range(count):
                    scale_factor = 1 - (i * 0.1)  
                    bedroom_area = area_per_room * scale_factor
                    length = (bedroom_area ** 0.5) * 1.5
                    width = bedroom_area / length
                    windows = 2 if i == 0 else 1  

                    dimension1[f'bedroom_{i+1}'] = {
                        'Area': bedroom_area,
                        'Width': width,
                        'Length': length,
                        'Windows': windows
                    }
            else:
                length = (area_per_room ** 0.5) * 1.5
                width = area_per_room / length
                dimension1[room] = {
                    'Area': area_per_room,
                    'Width': width,
                    'Length': length
                }
    
    if remaining_area > 0:
        for room in dimension1:
            additional_area = remaining_area * (dimension1[room]['Area'] / total_sq_ft)
            dimension1[room]['Area'] += additional_area
            length = (dimension1[room]['Area'] ** 0.5) * 1.5
            dimension1[room]['Width'] = dimension1[room]['Area'] / length
            dimension1[room]['Length'] = length
    
    return dimension1

total_sq_ft = float(input("Enter the total Sq feet Area : "))
input_text = "i want 2 bedrooms 2 toilets 1 kitchen 1 drawing room , 1 pooja room and 1 common balcony."

room_requirements = extract_pattern(input_text)
dimension = calculate_dimensions(total_sq_ft, room_requirements)

print(room_requirements)

print(dimension)
