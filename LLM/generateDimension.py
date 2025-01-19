import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Google API key not found. Please set the GOOGLE_API_KEY environment variable in the .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

def generate_layout(Sq_ft, requirement):
    prompt = f"""You are an expert architect. A user has provided the following details for a house:
        - Total square footage: {Sq_ft} sq ft
        - Requirements: {requirement}

        For each room type, please provide the following in **strict JSON format only** without any additional text before or after:
            1. Area allocation for each room type (if more than one, use "<room_type>_<number>"). 
            2. Width and length of the house for each room type.
            3. Minimum and maximum aspect ratios for each room type.
        
        The response should look like this:
        {{
            "rooms": [
                {{
                    "room_type": "bedroom_1",
                    "area": 150, 
                    "width": 12, 
                    "length": 12.5, 
                    "min_aspect_ratio": 1.2, 
                    "max_aspect_ratio": 1.5
                }}
            ]
        }}
        
        You must provide the response in pure JSON format without any code fences, additional text, or explanations.
        Ensure that the JSON is valid and does not contain any syntax errors."""

    try:

        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        
        response = model.generate_content(
            contents=[prompt],
        )
        
        layout = json.loads(response.text)
        return layout
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print("LLM Response:")
        print(response.text)
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    Sq_ft = 1000
    requirement = "3 bedrooms, 2 bathrooms, 1 kitchen, 1 living room"

    layout = generate_layout(Sq_ft, requirement)
    if layout:
        # dict = json.dumps(layout)
        print(layout)
        print(type(layout))

        rooms = layout.get("rooms", [])
        
        for room in rooms:
            room_type = room.get("room_type", "Unknown room type")
            area = room.get("area", "Unknown area")
            width = room.get("width", "Unknown width")
            length = room.get("length", "Unknown length")
            min_aspect_ratio = room.get("min_aspect_ratio", "Unknown min ratio")
            max_aspect_ratio = room.get("max_aspect_ratio", "Unknown max ratio")

            print(f"Room Type: {room_type}")
            print(f"  Area: {area} sq ft")
            print(f"  Length: {length} ft")
            print(f"  Width: {width} ft")
            print(f"  Minimum Aspect Ratio: {min_aspect_ratio}")
            print(f"  Maximun Aspect Ratio: {max_aspect_ratio}")
            print("-" * 50)
