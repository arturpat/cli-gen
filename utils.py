import dataclasses
import json
import os
import platform
import re
import subprocess
from typing import List, Literal, Dict, Optional

import colorama
import openai
from colorama import Fore
from yaspin import yaspin
from yaspin.spinners import Spinners


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
    def __init__(self, system_prompt: str, temperature: float, functions: List = None,
                 model: str = "gpt-3.5-turbo"):
        self.model = model
        self.temperature = temperature
        # TODO extract functions list just from the name using signature and docstring
        self.functions = default_functions if not functions else functions
        self.messages: Optional[List[Dict[str, str]]] = None
        self.system_prompt = system_prompt

        self.generated_one_liners = []
        self.executed_one_liners = []
        colorama.init(autoreset=True)

    def initial_call(self):
        """
        The initial, "clean" chat call. Will reset the messages queue to the system prompt only.
        :return:
        """
        self.messages = [ChatMessage("system", self.system_prompt).__dict__]

        # Give the GPT some context about the system operated:
        self.messages.append(ChatMessage("system", f"System info: {self.get_system_info()}").__dict__)

        with yaspin(Spinners.flip, text="Initiating GPT...") as sp:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                # functions=self.functions,  # to be enabled with functions
            )
            # todo check response

    def _handle_chat_completion_call(self, prompt, role: str = "user"):
        with yaspin(Spinners.flip, text="Coming up with a nice answer...") as sp:
            os_name = platform.system() if platform.system() != "Darwin" else "Mac OS"
            prompt = f"Generate a terminal one-liner to {prompt} in {os_name}"
            self.messages.append(ChatMessage(role, prompt).__dict__)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                # functions=self.functions,  # to be enabled with functions
            )
        return response

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

    def ask_gpt(self, query):
        # TODO: consider including pwd in a call

        # If not initialized, make the initial call
        # We want to make it here to minimize startup time
        if not self.messages:
            self.initial_call()

        # Ask the question
        response = self._handle_chat_completion_call(query)
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
            print(Fore.GREEN + extracted_code)
            self.generated_one_liners.append(extracted_code)
            return extract_code_snipped(resp)
        except ValueError:
            print(Fore.RED + "No code returned")

    def fresh_start(self):
        self.initial_call()

    def print_executed_one_liners(self) -> None:
        print("Executed one-liners:")
        for line in self.executed_one_liners:
            print(line)

    def print_generated_one_liners(self) -> None:
        print("All generated one-liners:")
        for line in self.generated_one_liners:
            print(line)

    def execute(self, command):
        self.executed_one_liners.append(command)
        shell_output = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
        print(shell_output.stdout.decode("utf-8"))


def check_if_file_exists(file_path: str):
    """
    To be used by the gpt as an AI function. Currently, disabled due to problems with hallucinated calls.
    :param file_path:
    :return:
    """
    return str(os.path.exists(file_path))


def extract_code_snipped(gpt_answer: str) -> str:
    re_pattern = r"```.*\n*(.*)\n*```"
    finds = re.search(re_pattern, gpt_answer)
    if not finds:
        # despite the initial prompt, sometimes the answer is given as a single line, containing only code
        if len(gpt_answer.split("\n")) == 1 and help_refusal_text not in gpt_answer:
            # in such case, we will only accept it if there are no new lines and the answer does not contain
            # refusal to provide answer
            return gpt_answer

        # Nothing found and the answer is not a bare one-liner:
        print(gpt_answer)
        raise ValueError("No code found")
    return finds.group(1)
