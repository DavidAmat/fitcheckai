import openai
import os

import time
import json
from dotenv import load_dotenv
from assistant_manager import AssistantManager, PROMPT

load_dotenv()

# OpenAI client setup
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

occasion = "Ibiza party"
PROMPT_OCCASION = f"""
"Use your expertise as outfit evaluator to rate the outfit in the image considering the occassion: {occasion}"
"""
image_path = "poc/01-gpt-api-image/ibiza1.jpg"

# Model configuration
manager = AssistantManager(model="gpt-4o", client=client)
manager.create_assistant(
    name="Look Expert",
    instructions=PROMPT,
)
manager.create_thread()

# Upload the image file and then add the image message
manager.upload_file(image_path=image_path)

# Add image message
manager.add_image_message()

manager.run_assistant(instructions=PROMPT_OCCASION)

manager.wait_for_completion()

summary = manager.get_summary()
print("Summary:")
print(summary)

print("Run Steps:")
print(json.dumps(manager.run_steps(), indent=4))
