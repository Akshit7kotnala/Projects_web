from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract
from googletrans import Translator
import os

app = Flask(__name__)

# Set upload folder and max file size
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max file size 16MB

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

translator = Translator()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to serve the HTML frontend
@app.route('/')
def index():
    return render_template('index.html')

# Route for image upload and translation
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if an image is included in the request
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        language = request.form['language']

        # Validate that a file was selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Validate the file type
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        # Save the image file to the server
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        print(f"Saving image to: {image_path}")  # Debugging log
        file.save(image_path)

        # Open the image and perform OCR to extract text
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"OCR error: {str(e)}")
            return jsonify({"error": f"OCR error: {str(e)}"}), 500

        # Translate the extracted text to the desired language
        try:
            translation = translator.translate(text, dest=language)
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return jsonify({"error": f"Translation error: {str(e)}"}), 500

        # Return the original and translated text in JSON format
        return jsonify({
            "original_text": text,
            "translated_text": translation.text
        })

    except Exception as e:
        print(f"Error: {str(e)}")  # Log error to console
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
