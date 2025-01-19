import json
from PIL import Image, ImageDraw, ImageFont
from entities import priority_order
from relationshipDot import placement_dict
from store import get_latest_data
import math

latest_data = get_latest_data()
room_types = latest_data.get('room_types', [])
 = list(set(priority_order)&set(room_types) )


TOTAL_AREA_SQFT = 1200
SCALE = 0.2
IMAGE_SIZE = 800
MARGIN = 20
FONT_SIZE = 14

image = Image.new('RGB', (IMAGE_SIZE, IMAGE_SIZE), 'white')
draw = ImageDraw.Draw(image)

try:
    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
except IOError:
    font = ImageFont.load_default()

def get_room_dimensions(room):
    area = room['area']
    min_ratio = room['min_aspect_ratio']
    max_ratio = room['max_aspect_ratio']
    aspect_ratio = (min_ratio + max_ratio) / 2
    width = math.sqrt(area * aspect_ratio)
    height = math.sqrt(area / aspect_ratio)
    width_px = int(width * SCALE)
    height_px = int(height * SCALE)
    return width_px, height_px

def get_room_color(room_type):
    if "pooja_room" in room_type:
        return "lightgreen"
    elif "bedroom" in room_type:
        return "lightcoral"
    elif "toilet" in room_type or "bathroom" in room_type:
        return "lightgray"
    elif "kitchen" in room_type:
        return "lightyellow"
    elif "study_room" in room_type:
        return "lightblue"
    elif "drawing_room" in room_type:
        return "lightpink"
    elif "balcony" in room_type:
        return "lightcyan"
    else:
        return "lightblue"

def draw_direction(room, font, draw):
    directions = room.get('directions', [])
    center_x, center_y = room['position']['center']
    offset = 20
    for direction in directions:
        if direction == "N":
            draw.polygon([
                (center_x, center_y - offset),
                (center_x - 5, center_y - offset + 10),
                (center_x + 5, center_y - offset + 10)
            ], fill='black')
        elif direction == "NE":
            draw.polygon([
                (center_x + offset / 1.414, center_y - offset / 1.414),
                (center_x + offset / 1.414 - 5, center_y - offset / 1.414 + 5),
                (center_x + offset / 1.414 + 5, center_y - offset / 1.414 + 5)
            ], fill='black')
        elif direction == "E":
            draw.polygon([
                (center_x + offset, center_y),
                (center_x + offset - 10, center_y - 5),
                (center_x + offset - 10, center_y + 5)
            ], fill='black')
        elif direction == "SE":
            draw.polygon([
                (center_x + offset / 1.414, center_y + offset / 1.414),
                (center_x + offset / 1.414 - 5, center_y + offset / 1.414 - 5),
                (center_x + offset / 1.414 + 5, center_y + offset / 1.414 - 5)
            ], fill='black')
        elif direction == "S":
            draw.polygon([
                (center_x, center_y + offset),
                (center_x - 5, center_y + offset - 10),
                (center_x + 5, center_y + offset - 10)
            ], fill='black')
        elif direction == "SW":
            draw.polygon([
                (center_x - offset / 1.414, center_y + offset / 1.414),
                (center_x - offset / 1.414 + 5, center_y + offset / 1.414 - 5),
                (center_x - offset / 1.414 - 5, center_y + offset / 1.414 - 5)
            ], fill='black')
        elif direction == "W":
            draw.polygon([
                (center_x - offset, center_y),
                (center_x - offset + 10, center_y - 5),
                (center_x - offset + 10, center_y + 5)
            ], fill='black')
        elif direction == "NW":
            draw.polygon([
                (center_x - offset / 1.414, center_y - offset / 1.414),
                (center_x - offset / 1.414 + 5, center_y - offset / 1.414 + 5),
                (center_x - offset / 1.414 - 5, center_y - offset / 1.414 + 5)
            ], fill='black')

common_rooms = [room['room_type'] for room in placement_dict['Dimensions'] if room['room_type'] in priority_order]
num_rooms = len(common_rooms)
GRID_COLS = math.ceil(math.sqrt(num_rooms))
GRID_ROWS = math.ceil(num_rooms / GRID_COLS)
cell_width = (IMAGE_SIZE - (GRID_COLS + 1) * MARGIN) / GRID_COLS
cell_height = (IMAGE_SIZE - (GRID_ROWS + 1) * MARGIN) / GRID_ROWS
placed_count = 0
for room_type in priority_order:
    room = next((item for item in placement_dict['Dimensions'] if item['room_type'] == room_type), None)
    if not room:
        print(f"Room '{room_type}' not found in placement_dict. Skipping.")
        continue
    row = placed_count // GRID_COLS
    col = placed_count % GRID_COLS
    if row >= GRID_ROWS:
        print(f"No more grid cells available to place room '{room_type}'. Skipping.")
        continue
    cell_x = MARGIN + col * (cell_width + MARGIN)
    cell_y = MARGIN + row * (cell_height + MARGIN)
    room_width, room_height = get_room_dimensions(room)
    if room_width > cell_width - 2 * MARGIN or room_height > cell_height - 2 * MARGIN:
        scale_factor = min((cell_width - 2 * MARGIN) / room_width, (cell_height - 2 * MARGIN) / room_height)
        room_width = int(room_width * scale_factor)
        room_height = int(room_height * scale_factor)
    room_x = cell_x + (cell_width - room_width) / 2
    room_y = cell_y + (cell_height - room_height) / 2
    top_left = (int(room_x), int(room_y))
    bottom_right = (int(room_x + room_width), int(room_y + room_height))
    room_color = get_room_color(room_type)
    draw.rectangle([top_left, bottom_right], outline='black', fill=room_color)
    text = room_type.replace('_', ' ').title()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = room_x + (room_width - text_width) / 2
    text_y = room_y + (room_height - text_height) / 2
    draw.text((int(text_x), int(text_y)), text, fill='black', font=font)
    draw_direction(room, font, draw)
    room['position'] = {
        "top_left": top_left,
        "bottom_right": bottom_right,
        "center": (int((top_left[0] + bottom_right[0]) / 2), int((top_left[1] + bottom_right[1]) / 2))
    }
    placed_count += 1

draw.rectangle([0, 0, IMAGE_SIZE-1, IMAGE_SIZE-1], outline='red', width=2)

for room in placement_dict['Dimensions']:
    if 'position' not in room:
        continue
    for neighbor in room['neighbors']:
        neighbor_room = next((r for r in placement_dict['Dimensions'] if r['room_type'] == neighbor['room_type']), None)
        if neighbor_room and 'position' in neighbor_room:
            thickness = max(1, neighbor['relationship_score'] // 50)
            draw.line([room['position']['center'], neighbor_room['position']['center']], fill='red', width=thickness)

image.save('floor_plan.png')
print("Floor plan saved as 'floor_plan.png'.")

image.show()
