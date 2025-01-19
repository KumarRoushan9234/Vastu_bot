from PIL import Image, ImageDraw, ImageFont

def draw_room(draw, top_left, dimensions, label):
    x, y = top_left
    width, height = dimensions
    draw.rectangle([x, y, x + width, y + height], outline="black", width=2)
    draw.text((x + 10, y + 10), label, fill="black")

def generate_layout_image(data):

    img_width = 500
    img_height = 500

    img = Image.new('RGB', (img_width, img_height), color = 'white')
    draw = ImageDraw.Draw(img)
    
    positions = {
        "bedrooms": [(50, 50), (200, 50)],
        "kitchen": (50, 200),
        "toilets": [(200, 200)]
    }

    for i, bedroom in enumerate(data['bedrooms']):
        position = positions['bedrooms'][i]
        draw_room(draw, position, (bedroom['width'] * 10, bedroom['length'] * 10), f"Bedroom {i+1}")

    kitchen = data['kitchen']
    draw_room(draw, positions['kitchen'], (kitchen['width'] * 10, kitchen['length'] * 10), "Kitchen")

    for i, toilet in enumerate(data['toilets']):
        position = positions['toilets'][i]
        draw_room(draw, position, (toilet['width'] * 10, toilet['length'] * 10), f"Toilet {i+1}")

    img.save('layout.png')

# Example dict
data = {
    "bedrooms": [
        {"area": 120, "length": 12, "width": 10, "min_aspect_ratio": 1.2, "max_aspect_ratio": 1.5},
        {"area": 100, "length": 10, "width": 10, "min_aspect_ratio": 1.0, "max_aspect_ratio": 1.2}
    ],
    "kitchen": {"area": 80, "length": 8, "width": 10, "min_aspect_ratio": 0.8, "max_aspect_ratio": 1.0},
    "toilets": [
        {"area": 30, "length": 5, "width": 6, "min_aspect_ratio": 0.83, "max_aspect_ratio": 1.0}
    ]
}

generate_layout_image(data)
