import openai
import os
import json
from dotenv import load_dotenv
from assistant_manager import AssistantManager
import io

load_dotenv()

# OpenAI client setup
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI()


class UserInterface:
    def __init__(self, client, model, occasion):
        self.manager = AssistantManager(model=model, client=client)
        self.occasion = occasion
        self.prompt = f"Use your expertise as outfit evaluator to rate the outfit in the image considering the occasion: {occasion}"

    def setup_assistant(self):
        self.manager.create_assistant(
            name="Look Expert",
            instructions=self.prompt,
        )
        self.manager.create_thread()

    def upload_image(
        self, image_path=None, image_binary: io.BufferedReader = None, file_id=None, with_message: str = None
    ):

        # Image (check if the file_id is already set, indicating the image is already uploaded)
        if file_id is None:
            # If the image is already in binary format, use it directly
            if image_binary is None:
                self.manager.upload_file(file_handle=image_binary)
            else:
                # Otherwise read the path
                self.manager.upload_file(file_handle=open(image_path, "rb"))

        # Submit message
        self.manager.add_image_message(
            with_message=with_message,
            file_id=file_id,
        )

    def add_text_message(self, message):
        self.manager.add_message_to_thread(role="user", content=message)

    def run_assistant(self):
        self.manager.run_assistant(instructions=self.prompt)
        self.manager.wait_for_completion()
        summary = self.manager.get_summary()
        metadata = [step.to_dict() for step in self.manager.run_steps()]
        return summary, metadata


if __name__ == "__main__":
    # file_id = "file-wLbsLZ2Ch4jb7tK4zyzftSve"
    ui = UserInterface(client=client, model="gpt-4o-mini", occasion="Ibiza party")
    ui.setup_assistant()
    image_path = "poc/01-gpt-api-image/f_party.jpg"
    ui.upload_image(image_path=image_path)
    summary, metadata = ui.run_assistant()

    print("##" * 20)
    print("           Summary (ChatGPT Mini 4o) ")
    print("##" * 20)
    print(summary)
    print("##" * 20)
    print("           Metadata ")
    print("##" * 20)
    print(json.dumps(metadata, indent=4))

    # Example of adding a text message to the same thread
    ui.add_text_message("What if I replace the glasses by other ones? Which style would you recommend?")
    summary2, metadata2 = ui.run_assistant()

    print("##" * 20)
    print("           Summary2 ")
    print("##" * 20)
    print(summary2)
    print("##" * 20)
    print("           Metadata2 ")
    print("##" * 20)
    print(json.dumps(metadata2, indent=4))
