from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorException
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os, base64, json, requests
from flask import Flask, render_template, request

# Load system variables with dotenv
from dotenv import load_dotenv
load_dotenv()

# Load keys
COGSVCS_CLIENTURL = https: // northcentralus.api.cognitive.microsoft.com/
COGSVCS_KEY = b6ad94a507ae41a2bdbd2ee3ad27de8f

# Create vision_client
vision_credentials = CognitiveServicesCredentials(COGSVCS_KEY)
vision_client = ComputerVisionClient(COGSVCS_CLIENTURL, vision_credentials)

# Create face_client

# Create the application
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/translate", methods=["GET", "POST"])
def translate():
    # Load image or placeholder
    image = get_image(request)

    # Set the default for language translation
    target_language = "en"
    if request.form and "target_language" in request.form:
        target_language = request.form["target_language"]

    # If it"s a GET, just return the form
    if request.method == "GET":
        return render_template("translate.html", image_uri=image.uri, target_language=target_language)

    # Create a placeholder for messages
    messages = []

    # TODO: Add code to retrieve text from picture
    messages = extract_text_from_image(image.blob, vision_client)

    # TODO: Add code to translate text
    messages = translate_text(
        messages, target_language, COGSVCS_KEY, COGSVCS_REGION)

    return render_template("translate.html", image_uri=image.uri, target_language=target_language, messages=messages)

@app.route("/train", methods=["GET", "POST"])
def train():
    # Load image or placeholder
    image = get_image(request)

    # If it"s a GET, just return the form
    if request.method == "GET":
        return render_template("train.html", image_uri=image.uri)

    # Retrieve name from form
    name = ""
    if "name" in request.form:
        name = request.form["name"]

    # Placeholder for messages
    messages = []

    # TODO: Add code to create or update person


    if not messages:
        messages.append("I don't recognize anyone")

    return render_template("train.html", messages=messages, image_uri=image.uri)

@app.route("/detect", methods=["GET", "POST"])
def detect():
    # Load image or placeholder
    image = get_image(request)

    # If it"s a GET, just return the form
    if request.method == "GET":
        return render_template("detect.html", image_uri=image.uri)

    # Placeholder for message
    messages = []

    # TODO: Add code to detect people in picture

    return render_template("detect.html", messages=messages, image_uri=image.uri)

def get_image(request):
    # Helper class 
    from image import Image
    if request.files:
        return Image(request.files["file"])
    else:
        return Image()


# Function that extracts text from images

def extract_text_from_image(image, client):
    try:
        result = client.recognize_printed_text_in_stream(image=image)

        lines = []
        if len(result.regions) == 0:
            lines.append("Photo contains no text to translate")

        else:
            for line in result.regions[0].lines:
                text = " ".join([word.text for word in line.words])
                lines.append(text)

        return lines

    except ComputerVisionErrorException as e:
        return ["Computer Vision API error: " + e.message]


def translate_text(lines, target_language, key, region):
    uri = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&to=" + target_language

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-type': 'application/json'
    }

    input = []

    for line in lines:
        input.append({"text": line})

    try:
        response = requests.post(uri, headers=headers, json=input)
        response.raise_for_status()  # Raise exception if call failed
        results = response.json()

        translated_lines = []

        for result in results:
            for translated_line in result["translations"]:
                translated_lines.append(translated_line["text"])

        return translated_lines

    except requests.exceptions.HTTPError as e:
        return ["Error calling the Translator Text API: " + e.strerror]

    except Exception as e:
        return ["Error calling the Translator Text API"]
