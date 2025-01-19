from pyautocad import Autocad, APoint

# Initialize AutoCAD application
acad = Autocad(create_if_not_exists=True)
print("Connected to AutoCAD")

# Function to clear existing objects in the model space
def clear_model_space():
    try:
        for obj in acad.iter_objects():
            obj.Delete()
        print("Cleared previous drawings from the model space.")
    except Exception as e:
        print(f"Error clearing model space: {e}")

# Clear previous drawings
clear_model_space()

# Room layout data
room_data = {
    'Dimension': [
        {'room_type': 'bedroom_1', 'area': 150, 'width': 12.25, 'length': 12.25, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
        {'room_type': 'bedroom_2', 'area': 150, 'width': 12.25, 'length': 12.25, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
        {'room_type': 'bedroom_3', 'area': 150, 'width': 12.25, 'length': 12.25, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
        {'room_type': 'dining_room', 'area': 150, 'width': 10, 'length': 15, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
        {'room_type': 'kitchen', 'area': 150, 'width': 10, 'length': 15, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
        {'room_type': 'living_room', 'area': 300, 'width': 17.32, 'length': 17.32, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
        {'room_type': 'toilet_1', 'area': 50, 'width': 5, 'length': 10, 'min_aspect_ratio': 1, 'max_aspect_ratio': 2.0},
        {'room_type': 'toilet_2', 'area': 50, 'width': 5, 'length': 10, 'min_aspect_ratio': 1, 'max_aspect_ratio': 2.0}
    ]
}

# Function to draw each room in AutoCAD
def draw_room(start_point, width, length, room_name, text_size=20):
    p1 = start_point
    p2 = APoint(p1.x + width, p1.y)
    p3 = APoint(p2.x, p2.y + length)
    p4 = APoint(p1.x, p1.y + length)

    # Draw rectangle for the room
    acad.model.AddLine(p1, p2)
    acad.model.AddLine(p2, p3)
    acad.model.AddLine(p3, p4)
    acad.model.AddLine(p4, p1)

    # Add room name in the center with adjusted font size
    text_position = APoint(p1.x + width / 2, p1.y + length / 2)
    acad.model.AddText(room_name, text_position, text_size)
    print(f"Created {room_name} with larger text size.")

# Start position and spacing
start_x, start_y = 0, 0
spacing_x, spacing_y = 5, 5  # Spacing between rooms

# Layout configuration
layout_structure = [
    ['bedroom_1', 'bedroom_2'],
    ['living_room'],
    ['dining_room', 'kitchen'],
    ['toilet_1', 'toilet_2']
]

# Draw layout based on configuration
for row in layout_structure:
    start_x_row = start_x  # Reset x for each new row
    max_length_in_row = 0  # Track row height for proper spacing
    
    for room_type in row:
        # Find the room details from room_data
        room = next((r for r in room_data['Dimension'] if r['room_type'] == room_type), None)
        if room:
            width = room['width']
            length = room['length']
            
            # Draw the room
            start_point = APoint(start_x_row, start_y)
            draw_room(start_point, width, length, room_type, text_size=30)
            
            # Update x position for next room in the row
            start_x_row += width + spacing_x
            # Update max_length_in_row to the tallest room in the row
            max_length_in_row = max(max_length_in_row, length)
    
    # Update y position for the next row of rooms
    start_y += max_length_in_row + spacing_y

print("Architectural house layout created successfully.")


# import matplotlib.pyplot as plt
# import matplotlib.patches as patches

# # Room data from the API
# rooms = [
#     {'room_type': 'bedroom_1', 'area': 150, 'width': 12.25, 'length': 12.25, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
#     {'room_type': 'bedroom_2', 'area': 150, 'width': 12.25, 'length': 12.25, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
#     {'room_type': 'bedroom_3', 'area': 150, 'width': 12.25, 'length': 12.25, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
#     {'room_type': 'dining_room', 'area': 150, 'width': 10, 'length': 15, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
#     {'room_type': 'kitchen', 'area': 150, 'width': 10, 'length': 15, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
#     {'room_type': 'living_room', 'area': 300, 'width': 17.32, 'length': 17.32, 'min_aspect_ratio': 1, 'max_aspect_ratio': 1.5},
#     {'room_type': 'toilet_1', 'area': 50, 'width': 5, 'length': 10, 'min_aspect_ratio': 1, 'max_aspect_ratio': 2.0},
#     {'room_type': 'toilet_2', 'area': 50, 'width': 5, 'length': 10, 'min_aspect_ratio': 1, 'max_aspect_ratio': 2.0}
# ]

# # Total area available (in sqft)
# total_area = 1200

# # Sum of the areas of the rooms
# total_room_area = sum(room['area'] for room in rooms)

# # Scale factor to adjust room dimensions to fit within total_area
# scale_factor = (total_area / total_room_area) ** 0.5  # Proportional scaling

# # Scale room dimensions based on the scale factor
# for room in rooms:
#     room['width'] *= scale_factor
#     room['length'] *= scale_factor
#     room['area'] = room['width'] * room['length']  # Update the area based on the new dimensions

# # Grid parameters
# rooms_per_row = 3  # Number of rooms per row
# padding = 2  # Padding between rooms

# # Create a figure and axis
# fig, ax = plt.subplots(figsize=(15, 15))

# # Initialize x_offset and y_offset for grid layout
# x_offset = 0
# y_offset = 0

# # Add room rectangles to the grid
# for i, room in enumerate(rooms):
#     width = room['width']
#     length = room['length']
    
#     # Create a rectangle for each room
#     ax.add_patch(patches.Rectangle((x_offset, y_offset), width, length, linewidth=1, edgecolor='black', facecolor='lightgray'))
    
#     # Add room label
#     ax.text(x_offset + width / 2, y_offset + length / 2, room['room_type'], 
#             horizontalalignment='center', verticalalignment='center', fontsize=10)

#     # Update x_offset for next room in the same row
#     x_offset += width + padding

#     # If the number of rooms per row is reached, move to the next row
#     if (i + 1) % rooms_per_row == 0:
#         x_offset = 0  # Reset x_offset for the new row
#         y_offset += max(room['length'] for room in rooms) + padding  # Increase y_offset for the new row

# # Set limits and labels
# ax.set_xlim(0, sum(room['width'] + padding for room in rooms[:rooms_per_row]))  # total width for the first row
# ax.set_ylim(0, y_offset + max(room['length'] for room in rooms))  # height of the grid

# ax.set_aspect('equal', 'box')
# ax.axis('off')  # Turn off axis
# plt.title('Room Layout within 1200 sqft', fontsize=16)

# # Show the plot
# plt.show()
