import re
from difflib import get_close_matches

# Predefined valid room types with their standardized names
valid_rooms = {
    'bedroom': 'bedroom',
    'toilet': 'toilet',
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

# Extract and Map Room Requirements
def extract_and_map_room_requirements(text, valid_rooms):
    room_dict = {}
    pattern = r'(\d+)\s+([a-zA-Z\s]+?)(?:\s+and\s+|,|$)'
    matches = re.findall(pattern, text)
    
    for number, room_type in matches:
        room_type = room_type.strip().lower()
        standardized_room_type = get_close_matches(room_type, valid_rooms.keys(), n=1, cutoff=0.6)
        if standardized_room_type:
            key = valid_rooms[standardized_room_type[0]]
            room_dict[key] = int(number)
    
    return room_dict

# Calculate Different Types of Room Dimensions
def calculate_room_dimensions(total_sq_ft, room_dict):
    allocation = {
        'bedroom': 0.20,
        'kitchen': 0.10,
        'toilet': 0.07,
        'garage': 0.12,
        'guest_room': 0.10,
        'living_room': 0.18,
        'corridor': 0.10
    }
    
    room_dimensions = {}
    
    for room, count in room_dict.items():
        if room in allocation:
            area_per_room = allocation[room] * total_sq_ft / count
        else:
            area_per_room = 0.05 * total_sq_ft / count
            
        # Standard Dimensions
        length_standard = (area_per_room ** 0.5) * 1.5
        width_standard = area_per_room / length_standard
        min_aspect_ratio_standard = width_standard / length_standard
        max_aspect_ratio_standard = length_standard / width_standard
        
        # Optimized Dimensions (assuming optimization changes dimensions slightly)
        length_optimized = length_standard * 0.9
        width_optimized = width_standard * 1.1
        min_aspect_ratio_optimized = width_optimized / length_optimized
        max_aspect_ratio_optimized = length_optimized / width_optimized
        
        # Custom Dimensions (flexible)
        length_custom = length_standard * 1.2
        width_custom = width_standard * 0.8
        min_aspect_ratio_custom = width_custom / length_custom
        max_aspect_ratio_custom = length_custom / width_custom
        
        # Store results in a dictionary
        room_dimensions[room] = {
            'Standard Dimensions': {
                'Area': area_per_room,
                'Width': width_standard,
                'Length': length_standard,
                'Min Aspect Ratio': min_aspect_ratio_standard,
                'Max Aspect Ratio': max_aspect_ratio_standard
            },
            'Optimized Dimensions': {
                'Area': area_per_room,
                'Width': width_optimized,
                'Length': length_optimized,
                'Min Aspect Ratio': min_aspect_ratio_optimized,
                'Max Aspect Ratio': max_aspect_ratio_optimized
            },
            'Custom Dimensions': {
                'Area': area_per_room,
                'Width': width_custom,
                'Length': length_custom,
                'Min Aspect Ratio': min_aspect_ratio_custom,
                'Max Aspect Ratio': max_aspect_ratio_custom
            }
        }
    
    return room_dimensions

input_text = "I want 3 bedrooms, 2 toilets, 1 kitchen, 1 drawing room, 1 pooja room and 1 common balcony."
total_sq_ft = 3000

room_requirements = extract_and_map_room_requirements(input_text, valid_rooms)
room_dimensions = calculate_room_dimensions(total_sq_ft, room_requirements)

for room, dimensions in room_dimensions.items():
    print(f"Spaces: {room.replace('_', ' ').title()}")
    for dimension_type, dimension_values in dimensions.items():
        print(f"  {dimension_type}:")
        for key, value in dimension_values.items():
            print(f"    {key}: {value:.2f}")
    print("\n")
