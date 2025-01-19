import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

from prompts import descriptionPrompt, layoutPrompt

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable in the .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
CORS(app)

global_data = {
    "Sq_ft": None,
    "requirement": None,
    "layout": None
}


def generate_description():
    if not all([global_data["Sq_ft"], global_data["requirement"], global_data["layout"]]):
        return {"error": "Global variables 'Sq_ft', 'requirement', and 'layout' must be set by /generate_layout first."}, 400

    client_data = {
        "Sq_ft": global_data["Sq_ft"],
        "requirement": global_data["requirement"],
        "Layout": global_data["layout"],
    }

    formatted_prompt = descriptionPrompt.format(
        Sq_ft=client_data["Sq_ft"],
        requirement=client_data["requirement"],
        Layout=json.dumps(client_data["Layout"], indent=4) 
    )
    # print("Description Prompt:", formatted_prompt)

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        
        response = model.generate_content(
            contents=[formatted_prompt],
        )
        
        desc = response.text.strip()
        print(f"LLM Response: {desc}")

        try:
            description = json.loads(desc)

        except json.JSONDecodeError:
            # for non-JSON 
            return {"description": desc}, 200
        
        return description
    

    except json.JSONDecodeError as e:
        print(f"JSON parsing error in Description: {e}")
        return {"error": f"JSON parsing error: {e}"}, 400

    except Exception as e:
        print(f"An error occurred in Description: {e}")
        return {"error": str(e)}, 500

def generate_layout(Sq_ft, requirement):
    formatted_prompt = layoutPrompt.format( Sq_ft = Sq_ft, requirement = requirement )

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        
        response = model.generate_content(
            contents=[formatted_prompt],
        )
        layout = json.loads(response.text.strip())
        return layout
    
    except Exception as e:
        print(f"An error occurred in Layout: {e}")
        return {"error": str(e)}, 500

@app.route('/generate_layout', methods=['POST'])
def api_generate_layout():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON input."}), 400

        Sq_ft = data.get('Sq_ft')
        requirement = data.get('requirement')

        if Sq_ft is None or requirement is None:
            return jsonify({"error": "Both 'Sq_ft' and 'requirement' are required."}), 400

        try:
            Sq_ft = float(Sq_ft)
        except ValueError:
            return jsonify({"error": "'Sq_ft' must be a number."}), 400

        Sq_ft = Sq_ft * 0.6
        layout = generate_layout(Sq_ft, requirement)

        if isinstance(layout, dict) and "error" in layout:
            return jsonify(layout), 400

        # print("Generated Layout:", layout)
        # print("Layout Type:", type(layout))

        global_data["Sq_ft"] = Sq_ft
        global_data["requirement"] = requirement
        global_data["layout"] = layout

        return jsonify(layout), 200

    except Exception as e:
        print(f"An unexpected error occurred in /generate_layout: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate_description', methods=['Get'])
def api_generate_description():
    try:
        description = generate_description()

        if isinstance(description, dict) and "error" in description:
            return jsonify(description), 400

        # print("Generated Description:", description)
        # print("Description Type:", type(description))

        return jsonify(description), 200

    except Exception as e:
        print(f"An unexpected error occurred in /generate_description: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)