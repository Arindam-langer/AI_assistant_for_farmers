from flask import Flask, render_template, request, redirect, jsonify
import asyncio
import os
import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import aiofiles
import json
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from query_rag_with_memory import get_response, load_session, save_session

app = Flask(__name__)

# User credentials for login
USERNAME = "farmin2"
PASSWORD = "123"

# Load the pretrained model for plant disease detection
model = models.resnet50(pretrained=True)
num_inftr = model.fc.in_features
model.fc = nn.Linear(num_inftr, 4)
model.load_state_dict(torch.load('templates/model12.pth',map_location=torch.device("cpu"))) #model path
model.eval()

# Class names for plant disease detection
class_names = ['Apple Scab', 'Black Rot', 'Cedar Apple Rust', 'Healthy']

# Function to transform the image for model prediction
def transform_image(image_bytes):
    my_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)

# Function to get the prediction from the model
def get_prediction(image_bytes):
    tensor = transform_image(image_bytes=image_bytes)
    outputs = model.forward(tensor)
    _, prediction = torch.max(outputs, 1)
    return class_names[prediction]

# Descriptions for plant diseases
diseases = {
    "Healthy": "You don't need to worry because your plants are healthy, keep maintaining them!",
    "Apple Scab": "Apple scab affects the parts of the plant that are above the ground. The initial symptoms are found on the leaves, flowers, and fruit. Spots develop on the leaves until the leaves become deformed. Edges on leaves generally appears blistered and scaly with the border between healthy and diseased leaf tissue clearly visible. Some infected fruit is so damaged that it falls from the branch before the fruit ripens.",
    "Cedar Apple Rust": "Cedar apple rust, or CAR, is a strange fungal disease that affects apple and red cedar trees. This disease can quickly destroy apple trees and causes spots on the fruit. First appears on the foliage as small greenish-yellow spots that gradually enlarge, becoming orange-yellow to rust-colored with red ribbon. The undersides of the leaves begin to form lesions that produce spores.",
    "Black Rot": "The spread of black rot disease is caused by the fungus Gloeosporium sp and can be through air, water splashes and contaminated agricultural tools. Humidity factors and the lack of sunlight entering the plants cause fungi to grow quickly, especially during the rainy season like this. Over time, the spots widen and heavily infected leaves fall from the tree. Branches with black rot may infect other parts of the plant."
}

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/tester', methods=['POST', 'GET'])
def tester():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            return render_template("home.html")
        else:
            return "Login failed. ERROR 404"
   
@app.route('/home.html')
def home():
    return render_template("home.html")

@app.route('/getstarted.html')
def query():
    return render_template("getstarted.html")

@app.route('/about.html')
def about():
    return render_template("about.html")

@app.route('/contact.html')
def contact():
    return render_template("contact.html")

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    session_id = request.args.get('session_id')
    session, session_file = asyncio.run(load_session(session_id))
    
    response = get_response(user_text, session)
    
    asyncio.run(save_session(session, session_file))
    
    return response

@app.route('/predict', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file:
        img_bytes = file.read()
        prediction_name = get_prediction(img_bytes)
        return jsonify({'prediction': diseases.get(prediction_name, "Unknown disease detected")})

    return jsonify({'error': 'Unknown error'})

if __name__ == "__main__":
    app.run(debug=True)
