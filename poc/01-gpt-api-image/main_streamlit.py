import openai
import os
import base64
import streamlit as st
from dotenv import load_dotenv
from assistant_manager import AssistantManager

load_dotenv()

# OpenAI client setup
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

# Model configuration
model = "gpt-4o"

# Helper function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main():
    manager = AssistantManager(model=model, client=client)

    # Streamlit interface
    st.title("Image Evaluation Assistant")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    submit_button = st.button(label="Run Assistant")

    if submit_button and uploaded_file:
        image_base64 = encode_image_to_base64(uploaded_file.name)

        manager.create_assistant(
            name="Image Evaluator",
            instructions="You are a personal assistant that can provide evaluations and feedback on images.",
        )
        manager.create_thread()

        # Add image message
        manager.add_image_message(image_base64=image_base64)

        manager.run_assistant(instructions="Evaluate the image and provide feedback.")

        manager.wait_for_completion()

        summary = manager.get_summary()
        st.write(summary)

        st.text("Run Steps:")
        st.code(manager.run_steps(), line_numbers=True)

if __name__ == "__main__":
    main()
