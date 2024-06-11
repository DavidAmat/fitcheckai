import streamlit as st
from dotenv import load_dotenv
import os
import io
import base64
from user_interface import UserInterface
import openai
import random
import string

st.title("ChatGPT-like clone")

load_dotenv()


# Function to generate a random string
def generate_random_string(length=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


# OpenAI client setup
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

# Initialize the UserInterface
if "ui" not in st.session_state:
    st.session_state["ui"] = UserInterface(client=client, model="gpt-3.5-turbo", occasion="General chat")
    st.session_state["ui"].setup_assistant()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Track whether an image has been uploaded and processed
if "image_processed" not in st.session_state:
    st.session_state.image_processed = False

uploaded_file = st.file_uploader("Upload a picture", type=["jpg", "jpeg", "png"])

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if uploaded_file is not None and not st.session_state.image_processed:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        uploaded_file.seek(0)
        bytes_data = uploaded_file.read()

        # Generate a unique filename
        name = "image_name"
        unique_suffix = generate_random_string()
        file_name = f"{name}_{unique_suffix}.jpg"

        # Define the path
        file_path = os.path.join("/tmp", file_name)

        # Save the image
        with open(file_path, "wb") as file:
            file.write(bytes_data)

        print(f"Image saved to {file_path}")

        # Upload image and send message with image
        st.session_state["ui"].upload_image(image_path=file_path, with_message=prompt)
        st.session_state.messages.append({"role": "user", "content": "User uploaded this image with message:"})

        # Mark the image as processed
        st.session_state.image_processed = True

    else:
        # Send text message only
        print("Sending text message ONLY")
        st.session_state["ui"].add_text_message(prompt)

    # Run assistant and get the response
    summary, metadata = st.session_state["ui"].run_assistant()

    with st.chat_message("assistant"):
        st.markdown(summary)
    st.session_state.messages.append({"role": "assistant", "content": summary})
