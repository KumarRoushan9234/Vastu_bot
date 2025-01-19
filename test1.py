from pyautocad import Autocad, APoint

# Initialize AutoCAD connection
acad = Autocad(create_if_not_exists=True)
acad.prompt("Python-AutoCAD integration started...\n")

# Define the matrix (example: 2D list of points)
matrix = [
    [0, 0, 0],   # Point at origin
    [10, 0, 0],  # Point 10 units along x-axis
    [10, 10, 0], # Point at (10, 10, 0)
    [0, 10, 0]   # Point at (0, 10, 0)
]

# Iterate over the matrix and create points in AutoCAD
for point in matrix:
    x, y, z = point
    # Create AutoCAD point
    acad.model.AddPoint(APoint(x, y, z))
    # Optionally, add lines connecting points if you want to visualize them as a path