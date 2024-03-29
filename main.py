from flask import Flask, request, render_template, url_for,send_from_directory,session
import requests
import io
from PIL import Image
import os
import time
import json
import sqlite3
from datetime import datetime


API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": "Bearer INSERT HF TOKEN HERE"}

app = Flask(__name__)
app.secret_key = 'secret'



@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt is None:
            return "No prompt provided", 400
        payload = {"inputs": prompt}
        response = requests.post(API_URL, headers=headers, json=payload)
        image = Image.open(io.BytesIO(response.content))

        # Create a unique filename using a timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        image_path = os.path.join('static', f'images/{timestamp}.png')
        session['image_path'] = image_path
        image.save(image_path)

        # Connect to the SQLite database
        conn = sqlite3.connect('prompts_images.db')

        # Create a cursor object
        c = conn.cursor()

        # Execute an SQL statement to insert the user prompt and the output image into the table
        c.execute('''
            INSERT INTO prompts_images (prompt, image)
            VALUES (?, ?)
        ''', (prompt, image_path))

        # Commit the changes and close the connection
        conn.commit()

        return render_template('display_image.html', image_path=url_for('static', filename=f'images/{timestamp}.png'))
    else:
        return render_template('input_prompt.html')
    
@app.route('/download', methods=['POST'])
def download():
    # Get the image path from the session
    image_path = session.get('image_path')
    # Extract the filename from the image_path
    filename = os.path.basename(image_path)
    # Send the file from the directory as a download
    return send_from_directory('static/images', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(port=5001, debug=True)

