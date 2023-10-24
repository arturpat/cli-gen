import dataclasses
import json
import os
import platform
import re
import subprocess
import sys
from typing import List, Literal, Dict, Optional

import openai


@dataclasses.dataclass
class ChatMessage:
    role: Literal["system", "assistant", "user"]
    content: str


default_functions = []  # disabling temporarily due to unexpected hallucinations
#     {
#         "name": "check_if_file_exists",
#         "description": "Checks if a file with the given path exists",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "file_path": {
#                     "type": "string",
#                     "description": "Path to the file in question",
#                 },
#             },
#             "required": ["file_path"],
#         },
#     }
# ]

help_refusal_text = "I don't know how to help with that"


class ChatWithMemory:
    def __init__(self, api_key: str, system_prompt: str, temperature: float, functions: List = None,
                 model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        # TODO extract functions list just from the name using signature and docstring
        self.functions = default_functions if not functions else functions
        self.messages: Optional[List[Dict[str, str]]] = None
        self.system_prompt = system_prompt

    def initial_call(self):
        """
        The initial, "clean" chat call. Will reset the messages queue to the system prompt only.
        :return:
        """
        self.messages = [ChatMessage("system", self.system_prompt).__dict__]

        # Give the GPT some context about the system operated:
        self.messages.append(ChatMessage("system", f"System info: {self.get_system_info()}").__dict__)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            ## JUST TESTING
            # functions=self.functions,
            # function_call="none"
        )
        # todo check response

    @staticmethod
    def get_system_info():
        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "OS Release": platform.release(),
            "Architecture": platform.architecture()[0],
            "Machine": platform.machine(),
            "Node (Hostname)": platform.node(),
            "Processor Name": platform.processor() or "N/A"
        }
        return system_info

    def _handle_chat_completion_call(self, prompt, role: str = "user"):
        os_name = platform.system() if platform.system() != "Darwin" else "Mac OS"
        prompt = f"Generate a terminal one-liner to {prompt} in {os_name}"
        self.messages.append(ChatMessage(role, prompt).__dict__)
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            # functions=self.functions,
            ## JUST TESTING
            # function_call="none"
        )
        return response

    def ask_gpt(self, query):
        # If not initialized, make the initial call
        # We want to make it here to minimize startup time
        if not self.messages:
            self.initial_call()

        # Ask the question
        response = self._handle_chat_completion_call(query)
        # response = openai.ChatCompletion.create(
        #     model=self.model,
        #     messages=self.messages,
        #     temperature=self.temperature,
        #     functions=self.functions,)
        #     # function_call="auto")
        response_message = response["choices"][0]["message"]

        # Check if GPT wanted to call a function
        if not response_message.get("function_call"):
            self.messages.append(response["choices"][0]["message"])
            return response["choices"][0]["message"]["content"]
        else:
            print("Calling a function...")
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "check_if_file_exists": check_if_file_exists,  # TODO: be smarter about it
            }  # only one function in this example, but you can have multiple
            function_name = response_message["function_call"]["name"]
            function_to_call = available_functions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = function_to_call(file_path=function_args.get("file_path"))

            # Step 4: send the info on the function call and function response to GPT
            self.messages.append(response_message)  # extend conversation with assistant's reply
            self.messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
            second_response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature
            )  # get a new response from GPT where it can see the function response
            self.messages.append(second_response["choices"][0]["message"])
            return second_response["choices"][0]["message"]["content"]

    def ask_gpt_code_snippet_only(self, query):
        resp = self.ask_gpt(query=query)
        try:
            extracted_code = extract_code_snipped(resp)
            print(extracted_code)
            if get_y_n("Execute? (y/n)"):
                self.execute(extracted_code)
            return extract_code_snipped(resp)
        except ValueError:
            print("No code returned")

    @staticmethod
    def execute(command):
        shell_output = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        print(shell_output.stdout.decode("utf-8"))


def check_if_file_exists(file_path: str):
    return str(os.path.exists(file_path))


def extract_code_snipped(gpt_answer: str) -> str:
    re_pattern = r"```.*\n*(.*)\n*```"
    finds = re.search(re_pattern, gpt_answer)
    if not finds:
        print(gpt_answer)
        raise ValueError("No code found")
    # assert len(finds) == 1, "More than one code snipped found, bad bad GPT"
    return finds.group(1)


def get_y_n(input_text):
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = input(input_text).lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")