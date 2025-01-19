def extract_pattern(text):

  room_dict = {}

  pattern = r'(\d+)\s+([a-zA-Z\s]+)'

  matches = re.findall(pattern, text)

  for number, room_type in matches:

    key = room_type.strip().replace(" ", "_").lower()

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
    
    dimension1 = {}
    dimension2 = {}
    dimension3 = {}
    
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
        
        dimension1[room] = {
            'Area': area_per_room,
            'Width': width_standard,
            'Length': length_standard,
            'Min Aspect Ratio': min_aspect_ratio_standard,
            'Max Aspect Ratio': max_aspect_ratio_standard
        }
        
        # Optimized Dimensions (assuming optimization changes dimensions slightly)
        length_optimized = length_standard * 0.9
        width_optimized = width_standard * 1.1
        min_aspect_ratio_optimized = width_optimized / length_optimized
        max_aspect_ratio_optimized = length_optimized / width_optimized
        
        dimension2[room] = {
            'Area': area_per_room,
            'Width': width_optimized,
            'Length': length_optimized,
            'Min Aspect Ratio': min_aspect_ratio_optimized,
            'Max Aspect Ratio': max_aspect_ratio_optimized
        }
        
        # Custom Dimensions (flexible)
        length_custom = length_standard * 1.2
        width_custom = width_standard * 0.8
        min_aspect_ratio_custom = width_custom / length_custom
        max_aspect_ratio_custom = length_custom / width_custom
        
        dimension3[room] = {
            'Area': area_per_room,
            'Width': width_custom,
            'Length': length_custom,
            'Min Aspect Ratio': min_aspect_ratio_custom,
            'Max Aspect Ratio': max_aspect_ratio_custom
        }
    
    return dimension1, dimension2, dimension3



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
    
    dimension1 = {}
    
    for room, count in room_dict.items():
        if room in allocation:
            area_per_room = allocation[room] * total_sq_ft / count
        else:
            area_per_room = 0.05 * total_sq_ft / count
            
        if room == 'bedroom':
            # Assign different areas for each bedroom with decreasing size
            for i in range(count):
                scale_factor = 1 - (i * 0.1)  # Decrease area by 10% for each subsequent bedroom
                bedroom_area = area_per_room * scale_factor
                length = (bedroom_area ** 0.5) * 1.5
                width = bedroom_area / length
                min_aspect_ratio = width / length
                max_aspect_ratio = length / width
                windows = 2 if i == 0 else 1  # First bedroom gets 2 windows, others get 1 window

                dimension1[f'bedroom_{i+1}'] = {
                    'Area': bedroom_area,
                    'Width': width,
                    'Length': length,
                    'Min Aspect Ratio': min_aspect_ratio,
                    'Max Aspect Ratio': max_aspect_ratio,
                    'Windows': windows
                }
        else:
            dimension1[room] = {
                'Area': area_per_room,
                'Width': (area_per_room ** 0.5) * 1.5,
                'Length': area_per_room / ((area_per_room ** 0.5) * 1.5),
                'Min Aspect Ratio': (area_per_room / ((area_per_room ** 0.5) * 1.5)) / ((area_per_room ** 0.5) * 1.5),
                'Max Aspect Ratio': ((area_per_room ** 0.5) * 1.5) / (area_per_room / ((area_per_room ** 0.5) * 1.5))
            }
    
    return dimension1

# for the area at end not adding up

# Solution 1: Dynamic Adjustment of Allocation
# We can calculate the area of key rooms first, then allocate the remaining area to the other rooms based on their proportions.

# Solution 2: Normalization of Allocation Percentages
# We can normalize the allocation percentages so that they sum up to 1 (or 100%).