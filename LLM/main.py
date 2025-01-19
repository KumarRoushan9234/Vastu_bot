#  api => with Chat History
import os
import json
import re
import difflib  
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

from prompts import descriptionPrompt, layoutPrompt, chatPrompt
from store import save_to_json_file, get_latest_data

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable in the .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
CORS(app)

app_data = get_latest_data() or {
    "Sq_ft": 1200,
    "requirement": None,
    "layout": None,
    "client_entities": [],
    "chat_history": [
        {"role": "user", "parts": "Hello"},
        {"role": "model", "parts": "Great to meet you,I'm Vastu_ChatBot. What would you like to know?"}
    ],
    "time_history": [],
    "description": "",
}

entities = [
    "kitchen", "bedroom", "bathroom", "pooja_room", "living_room", "dining_room",
    "study_room", "storeroom", "balcony", "utility_room", "guest_room",
    "home_office", "nursery", "laundry_room", "garage", "library", "media_room", "playroom", "pet_room", "reading_room", "storage_room", "balcony_garden", "washroom",
]

# mapping variations
extended_entity_mapping = {
    "toilet": ["toilet", "washroom", "bathroom", "restroom", "wc"],
    "bedroom": ["bedroom", "bedrooms", "guestroom","guest room"],
    "living_room": ["living_room", "living room", "lounge"],
    "dining_room": ["dining_room", "dining room", "dining"],
    "kitchen": ["kitchen", "cooking area", "kitchenette"],
    "balcony": ["balcony", "balcony_garden"],
    "study_room": ["study_room", "studyroom", "home office", "office"],
    "storeroom": ["storeroom", "storage room", "storerooms"],
    "pooja_room": ["pooja_room", "puja room", "prayer room"],
    "utility_room": ["utility_room", "utility space", "service room"],
    "guest_room": ["guest_room", "guest room", "visitors room"],
    "nursery": ["nursery", "child's room", "kids room"],
    "laundry_room": ["laundry_room", "laundry", "wash room"],
    "garage": ["garage", "carport", "vehicle storage"],
    "library": ["library", "reading room", "book room"],
    "media_room": ["media_room", "home theater", "entertainment room"],
    "playroom": ["playroom", "children's play area", "play area"],
    "pet_room": ["pet_room", "pet space", "animal room"],
    "reading_room": ["reading_room", "study area", "book nook"],
    "storage_room": ["storage_room", "storeroom", "storage space"],
}

essential_components = ["bedroom", "toilet", "kitchen", "living_room", "dining_room", ]
# "bathroom", "utility_room", "storeroom", "hallway"

def is_similar(input_word, entity_word, threshold=0.7):
    similarity = difflib.SequenceMatcher(None, input_word, entity_word).ratio()
    return similarity >= threshold


def match_entities(user_input):
    matched_entities = set()
    
    entity_pattern = re.compile(r'(\d+)?\s*([a-zA-Z_]+)')
    
    for match in entity_pattern.finditer(user_input):
        number = match.group(1)
        entity = match.group(2).lower()


        for main_entity, variations in extended_entity_mapping.items():
            if any(is_similar(entity, variation) for variation in variations):
                
                if number:
                    matched_entities.add(f"{number} {main_entity}")
                else:
                    matched_entities.add(main_entity)
                break
    return matched_entities

def update_entities(new_entities):
    
    current_entities = {re.sub(r'\d+', '', entity): entity for entity in app_data['client_entities']}
    
    for new_entity in new_entities:
        entity_type = re.sub(r'\d+', '', new_entity)
        if entity_type in current_entities:
            
            app_data['client_entities'] = [entity if entity != current_entities[entity_type] else new_entity for entity in app_data['client_entities']]
        else:
            
            app_data['client_entities'].append(new_entity)


def check_essential_components(requirement):
    provided_components = [comp for comp in essential_components if comp in requirement.lower()]
    return provided_components


def generate_description():
    if not all([app_data["Sq_ft"], app_data["layout"]]):
        return {"error": "App data 'Sq_ft' and 'layout' must be set by /generate_layout first."}, 400

    client_data = {
        "Sq_ft": app_data["Sq_ft"],
        "client_entities": app_data["client_entities"],
        "Layout": app_data["layout"],
    }

    formatted_prompt = descriptionPrompt.format(
        Sq_ft=client_data["Sq_ft"],
        requirement=json.dumps(client_data["client_entities"]),
        Layout=json.dumps(client_data["Layout"], indent=4)
    )

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        response = model.generate_content(contents=[formatted_prompt])
        desc = response.text.strip()
        
        formatted_response = desc.replace("*", "").replace("#", "").replace("**", "").replace("##", "")


        try:
            description = json.loads(formatted_response)
        except json.JSONDecodeError:
            return {"description": formatted_prompt}, 200
        
        return description

    except Exception as e:
        return {"error": str(e)}, 500


def generate_layout(Sq_ft, requirement):
    formatted_prompt = layoutPrompt.format(Sq_ft=Sq_ft, requirement=json.dumps(requirement))
    
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        response = model.generate_content(contents=[formatted_prompt])
        layout = json.loads(response.text.strip())
        print(layout)
        return layout

    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/set_Sq_ft",methods=['POST'])
def set_Sq_ft():
    try:
        data = request.json
        if not data or "Sq_ft" not in data: 
            return jsonify({"error": "Sq_ft is required"}), 400
        
        app_data["Sq_ft"] = data["Sq_ft"]
        print("Sq_ft : ",data["Sq_ft"])

        save_to_json_file(app_data)
        return jsonify({"Sq_ft":data["Sq_ft"]}), 200
    
    except Exception as e:
        print(f"An unexpected error occurred /set_Sq_ft: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/chat', methods=['POST'])
def chat_with_model():
    try:
        data = request.json
        if not data or "user_input" not in data:
            return jsonify({"error": "Message is required"}), 400

        user_input = data.get("user_input").strip()
        if not user_input:
            return jsonify({"error": "Message cannot be empty"}), 400


        if 'client_entities' not in app_data:
            app_data['client_entities'] = []

        history = app_data.get("chat_history")
        time_history = app_data.get("time_history", [])


        matched_entities = match_entities(user_input)
        
        update_entities(matched_entities)
        
        print(f'Requirements : {app_data["client_entities"]}')

        # format => "YYYY-MM-DD[HH:MM:SS]"
        current_time = datetime.now().strftime("%Y-%m-%d[%H:%M:%S]")
        

        formatted_chatPrompt = chatPrompt.format(
            Sq_ft=app_data["Sq_ft"],
            client_entities=app_data["client_entities"],
            essential_components=essential_components,
            user_input=user_input
        )
        
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        chat = model.start_chat(history=history)
        
        response = chat.send_message(formatted_chatPrompt)

        formatted_response = response.text.replace("*", "")

        history.append({"role": "user", "parts": user_input})
        history.append({"role": "model", "parts": formatted_response})  
        app_data["chat_history"] = history  

        time_history.append(current_time)
        app_data["time_history"] = time_history

        save_to_json_file(app_data)

        return jsonify({"response": formatted_response, "history": history, "current_time": current_time, "time_history": time_history, "client_entities":app_data["client_entities"]}), 200

    
    except Exception as e:
        print(f"An unexpected error occurred in /chat: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/clear_data', methods=['POST'])
def clear_data():
    try:
        global app_data
        previous_appData = app_data
        app_data = {
            "Sq_ft": 1200,
            "requirement": None,
            "layout": None,
            "client_entities": [],
            "chat_history": [
                {"role": "user", "parts": "Hello"},
                {"role": "model", "parts": "Great to meet you. What would you like to know?"}
            ],
        }
        save_to_json_file(app_data)

        return jsonify({"Previous App Data":previous_appData,"message": "Data cleared successfully."}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/show_data', methods=['POST'])
def show_data():
    try:
        global app_data
        return jsonify({"App Data":app_data,"message": "Here is your App Data."}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/generate_layout', methods=['GET'])
def api_generate_layout():
    try:
        
        Sq_ft = app_data.get('Sq_ft')
        client_entities = app_data.get('client_entities', [])

        present_components = []
        
        for entity in client_entities:
            entity_type = re.sub(r'\d+', '', entity).strip()  
            if entity_type in essential_components:
                present_components.append(entity_type)
        
        missing_components = [component for component in essential_components if component not in present_components]

        if missing_components:
            return jsonify({
                "error": "Missing essential components.",
                "missing_components": missing_components
            }), 400

        if not Sq_ft or not client_entities:
            return jsonify({
                "error": "Insufficient data: Please make sure Sq_ft and client_entities are present."
            }), 400

        layout = generate_layout(Sq_ft, client_entities)
        if "error" in layout:
            return jsonify(layout), 500

        description = generate_description()
        if isinstance(description, dict) and "error" in description:
            return jsonify(description), 400

        app_data["layout"] = layout
        app_data["description"] = description

        save_to_json_file(app_data)

        return jsonify({
            "layout": layout,
            "description": description
        }), 200

    except Exception as e:
        print(f"An unexpected error occurred in /generate_layout: {e}")
        return jsonify({"error": str(e)}), 500

    

# @app.route('/generate_description', methods=['GET'])
# def api_generate_description():
#     description = generate_description()

#     if isinstance(description, dict) and "error" in description:
#         return jsonify(description), 400

#     return jsonify(description), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
