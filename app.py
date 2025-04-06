from flask import Flask, request, jsonify
import base64
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import os
from inference import (
    query_pill_features, query_drugs, query_side_effects, query_ddi
)

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'Pill ID Gemini API is running!'

@app.route('/analyze-both', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        image1_b64 = data.get('image1')
        image2_b64 = data.get('image2')
        if not image1_b64 or not image2_b64:
            return jsonify({'error': 'Both images are required'}), 400

        # Decode images and combine them
        image1_bytes = base64.b64decode(image1_b64)
        image2_bytes = base64.b64decode(image2_b64)
        image1 = Image.open(BytesIO(image1_bytes))
        image2 = Image.open(BytesIO(image2_bytes))
        total_height = image1.height + image2.height
        new_image = Image.new('RGB', (max(image1.width, image2.width), total_height))
        new_image.paste(image1, (0, 0))
        new_image.paste(image2, (0, image1.height))
        combined_image_bytes = BytesIO()
        new_image.save(combined_image_bytes, format='PNG')
        combined_image_bytes.seek(0)
        combined_image_bytes = combined_image_bytes.read()
        
        result = query_drugs(*query_pill_features(combined_image_bytes))
        print(result["1st choice"])
        return jsonify(result)
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/side-effects', methods=['GET'])
def get_side_effects():
    try:
        drug_name = request.args.get('drug_name')
        if not drug_name:
            return jsonify({'error': 'Drug name is required'}), 400
        side_effects = query_side_effects(drug_name)
        return jsonify({'side_effects': side_effects})
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/ddi', methods=['GET'])
def get_ddi():
    try:
        drug1_name = request.args.get('drug1_name')
        drug2_name = request.args.get('drug2_name')
        if not drug1_name or not drug2_name:
            return jsonify({'error': 'Both drug names are required'}), 400
        ddi_result = query_ddi(drug1_name, drug2_name)
        return jsonify({'ddi': ddi_result})
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test endpoint is working!'})

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)