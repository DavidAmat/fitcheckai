import streamlit as st
from io import BytesIO
from user_interface import UserInterface
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI client setup
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()

# Streamlit app logic
st.title("Outfit Evaluator Chatbot")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize the user interface
ui = UserInterface(client=client, model="gpt-4o", occasion="Ibiza party")
ui.setup_assistant()

# File uploader for image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
    if st.button("Submit Image"):
        # Convert the uploaded image to io.BufferedReader
        image_bytes = BytesIO(uploaded_file.read())
        ui.upload_image(image_binary=image_bytes)
        summary, metadata = ui.run_assistant()
        st.session_state.chat_history.append(("user", "Image uploaded for evaluation."))
        st.session_state.chat_history.append(("assistant", summary))

# Chat input box
user_input = st.text_input("Your message:", "")
if st.button("Send"):
    if user_input:
        ui.add_text_message(user_input)
        summary, metadata = ui.run_assistant()
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", summary))

# Display chat history
for role, message in st.session_state.chat_history:
    if role == "user":
        st.write(f"**You:** {message}")
    else:
        st.write(f"**Assistant:** {message}")

# File uploader for additional image
additional_uploaded_file = st.file_uploader("Choose another image...", type=["jpg", "jpeg", "png"], key="additional_image")

if additional_uploaded_file:
    st.image(additional_uploaded_file, caption='Additional Uploaded Image', use_column_width=True)
    additional_user_input = st.text_input("Message with the additional image:", "")
    if st.button("Submit Additional Image"):
        additional_image_bytes = BytesIO(additional_uploaded_file.read())
        ui.upload_image(image_binary=additional_image_bytes, with_message=additional_user_input)
        summary, metadata = ui.run_assistant()
        st.session_state.chat_history.append(("user", f"Image uploaded with message: {additional_user_input}"))
        st.session_state.chat_history.append(("assistant", summary))
