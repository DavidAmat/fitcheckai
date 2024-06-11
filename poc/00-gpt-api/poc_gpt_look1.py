from openai import OpenAI
import json
import os
import base64
from dotenv import load_dotenv

# Relative path
path = os.path.dirname(__file__)
os.chdir(path)  # Change the current working

# Load environment variables from the .env file
load_dotenv()

client = OpenAI()

# Use the local file 'handwrittensample.png'
image_path = "look1.png"

# Load the JSON schema
# invoice_schema = load_json_schema("invoice_schema.json")

# Open the local image file in binary mode
with open(image_path, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

response = client.chat.completions.create(
    model="g-3tYia2gms-well-dress-gpt",
    response_format={"type": "json_object"},
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "provide a technical fashion evaluation telling how well each of the following clothes suit my look and for which occasions/weather/sex it is suitable",
                },
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            ],
        }
    ],
    max_tokens=500,
)

print(response.choices[0].message.content)
json_data = json.loads(response.choices[0].message.content)
filename_without_extension = os.path.splitext(os.path.basename(image_path))[0]
json_filename = f"{filename_without_extension}.json"

with open(json_filename, "w") as file:
    json.dump(json_data, file, indent=4)

print(f"JSON data saved to {json_filename}")
