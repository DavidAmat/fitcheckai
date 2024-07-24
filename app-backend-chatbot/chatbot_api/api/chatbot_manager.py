import openai
import os
import time
import io
import json
from dotenv import load_dotenv
from datetime import datetime
import uuid


class ChatbotManager:
    def __init__(self, occasion: str = "not defined", model="gpt-4o-mini"):
        load_dotenv()
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        self.assistant_id = os.environ.get("ASSISTANT_ID")
        self.client = openai.OpenAI()
        self.model = model
        self.occasion = occasion
        self.prompt = f"Use your expertise as outfit evaluator to rate the outfit in the image considering the occasion: {occasion}"
        self.thread_id = None
        self.run_id = None
        self.file_id = None

    def setup_assistant(self):
        if self.assistant_id is not None:
            self.assistant = self.client.beta.assistants.retrieve(assistant_id=self.assistant_id)
            print(f"AssistantID: {self.assistant.id}")
        else:
            raise ValueError("Assistant ID not found")

    def create_thread(self) -> str:
        thread_response = self.client.beta.threads.create()
        self.thread_id = thread_response.id
        return self.thread_id

    def upload_image(self, image_binary: bytes, image_name: str = None) -> str:
        # Generate a random name for the image with the date timestamp as part of it plus random suffix
        # using datetime and uuid
        if image_name is None:
            date_ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            suff_rand = uuid.uuid4()
            image_name = f"look--{date_ts}--{suff_rand}.jpg"

        file_response = self.client.files.create(
            file=(image_name, io.BytesIO(image_binary), "image/jpeg"), purpose="vision"
        )
        self.file_id = file_response.id
        print(f"Uploaded File ID: {self.file_id}")
        return self.file_id

    def send_to_thread_message_with_image(self, thread_id, file_id, message):
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=[
                {
                    "type": "text",
                    "text": message,
                },
                {
                    "type": "image_file",
                    "image_file": {
                        "file_id": file_id,
                    },
                },
            ],
        )

    def create_run_thread(self, thread_id) -> str:
        run_response = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
            instructions=self.prompt,
        )
        self.run_id = run_response.id
        print(f"RunID: {self.run_id}")
        return self.run_id

    def wait_run_thread(self, thread_id, run_id):
        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            # print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

            if run_status.status == "completed":
                break
            elif run_status.status == "requires_action":
                print("Requires action...")
            time.sleep(1)

    def process_thread(self, thread_id):
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        last_message = messages.data[0]
        role = last_message.role
        response = last_message.content[0].text.value
        summary = response
        print(f"SUMMARY-----> {role.capitalize()}: ==> {response}")
        return summary

    def submit_image_with_text(self, image_binary: bytes, message: str, image_name: str = None):
        self.setup_assistant()
        thread_id = self.create_thread()
        file_id = self.upload_image(image_binary=image_binary, image_name=image_name)
        self.send_to_thread_message_with_image(thread_id=thread_id, file_id=file_id, message=message)
        run_id = self.create_run_thread(thread_id=thread_id)
        self.wait_run_thread(thread_id=thread_id, run_id=run_id)
        message_response = self.process_thread(thread_id=thread_id)
        result = {
            "response": message_response,
            "file_id": file_id,
            "thread_id": thread_id,
            "assistant_id": self.assistant_id,
            "run_id": run_id,
        }
        return result

    def submit_text(self, thread_id: str, message: str):
        self.setup_assistant()
        self.client.beta.threads.messages.create(thread_id=thread_id, role="user", content=message)
        run_id = self.create_run_thread(thread_id=thread_id)
        self.wait_run_thread(thread_id=thread_id, run_id=run_id)
        message_response = self.process_thread(thread_id=thread_id)
        result = {
            "response": message_response,
            "thread_id": thread_id,
            "assistant_id": self.assistant_id,
            "run_id": run_id,
        }
        return result

    @staticmethod
    def load_image_as_binary(image_path) -> bytes:
        with open(image_path, "rb") as image:
            image_bytes = image.read()
        return image_bytes


if __name__ == "__main__":
    image_path = "/home/david/Documents/data_science/projects/fitcheckai/poc/chatbot_api/scripts/look3.jpg"
    image_binary = ChatbotManager.load_image_as_binary(image_path)
    manager = ChatbotManager(occasion="Ibiza party")

    result = manager.submit_image_with_text(
        image_binary=image_binary,
        message="Is this appropriate for my party ?",
    )

    print("--" * 20)
    print("           Response ")
    print("--" * 20)
    print(result["response"])
    print(f"File_id: {result['file_id']}")
    print(f"Thread_id: {result['thread_id']}")
    print(f"Assistant_id: {result['assistant_id']}")
    print(f"Run_id: {result['run_id']}")
    print("--" * 20)

    thread_id = result["thread_id"]
    # Submit text to existing thread
    text_result = manager.submit_text(
        thread_id=thread_id,
        message="Am I wearing a clock? In which arm?",
    )
    print("--" * 20)
    print("           Response ")
    print("--" * 20)
    print(text_result["response"])
