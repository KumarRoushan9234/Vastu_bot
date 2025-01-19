import svgwrite

rooms = [
    {'room_type': 'bedroom_1', 'width': 120, 'height': 120},
    {'room_type': 'bedroom_2', 'width': 120, 'height': 120},
    {'room_type': 'kitchen', 'width': 100, 'height': 150},
    {'room_type': 'living_room', 'width': 200, 'height': 200},
]

dwg = svgwrite.Drawing('house_layout.svg', profile='tiny')

x_offset, y_offset = 10, 10
for room in rooms:
    dwg.add(dwg.rect((x_offset, y_offset), (room['width'], room['height']), fill='lightgray', stroke='black'))
    dwg.add(dwg.text(room['room_type'], insert=(x_offset + room['width']/4, y_offset + room['height']/2), fill='black'))

    x_offset += room['width'] + 10
    if x_offset + room['width'] > 600:
        x_offset = 10
        y_offset += max(room['height'] for room in rooms) + 10

dwg.save()
