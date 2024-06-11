import openai
import time
import io
from prompts import PROMPT1, PROMPT2, PROMPT_IMAGE

PROMPT = PROMPT2

class AssistantManager:
    thread_id = None
    assistant_id = "asst_hQspYDjXutgDxSsVJlSJeC69"

    def __init__(self, model: str, client: openai.OpenAI):
        self.client = client
        self.model = model
        self.assistant = None
        self.thread = None
        self.run = None
        self.summary = None
        self.file_id = None

        # Retrieve existing assistant and thread if IDs are already set
        if AssistantManager.assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(assistant_id=AssistantManager.assistant_id)
        if AssistantManager.thread_id:
            self.thread = self.client.beta.threads.retrieve(thread_id=AssistantManager.thread_id)

    def create_assistant(self, name, instructions):
        if not self.assistant:
            assistant_obj = self.client.beta.assistants.create(name=name, instructions=instructions, model=self.model)
            AssistantManager.assistant_id = assistant_obj.id
            self.assistant = assistant_obj
            print(f"AssistantID: {self.assistant.id}")

    def create_thread(self):
        if not self.thread:
            thread_obj = self.client.beta.threads.create()
            AssistantManager.thread_id = thread_obj.id
            self.thread = thread_obj
            print(f"ThreadID: {self.thread.id}")

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(thread_id=self.thread.id, role=role, content=content)

    def run_assistant(self, instructions):
        if self.thread and self.assistant:
            self.run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                instructions=instructions,
            )

    def process_message(self):
        if self.thread:
            messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            summary = []

            last_message = messages.data[0]
            role = last_message.role
            response = last_message.content[0].text.value
            summary.append(response)

            self.summary = "\n".join(summary)
            print(f"SUMMARY-----> {role.capitalize()}: ==> {response}")

    def get_summary(self):
        return self.summary

    def wait_for_completion(self):
        if self.thread and self.run:
            while True:
                time.sleep(5)
                run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.run.id)
                print(f"RUN STATUS:: {run_status.model_dump_json(indent=4)}")

                if run_status.status == "completed":
                    self.process_message()
                    break
                elif run_status.status == "requires_action":
                    print("Requires action...")

    def run_steps(self):
        run_steps = self.client.beta.threads.runs.steps.list(thread_id=self.thread.id, run_id=self.run.id)
        print(f"Run-Steps::: {run_steps}")
        return run_steps.data

    def upload_file(self, file_handle: io.BufferedReader):
        response = self.client.files.create(file=file_handle, purpose="vision")
        self.file_id = response.id
        print(f"Uploaded File ID: {self.file_id}")

    def add_image_message(self, with_message=None, file_id=None):
        if with_message is None:
            with_message = PROMPT_IMAGE

        if file_id:
            self.file_id = file_id

        if self.thread and self.file_id:
            # Add the message with the file_id of the uploaded image
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=[
                    {
                        "type": "text",
                        "text": with_message,
                    },
                    {"type": "image_file", "image_file": {"file_id": self.file_id}},
                ],
            )
