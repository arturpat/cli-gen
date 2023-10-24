import os
import re

import openai

from utils import ChatWithMemory, help_refusal_text

system_prompt = ("You are a terminal one-liner generator. Always encapsulate generated code with ```. Answer with "
                 f"either the one-liner or with '{help_refusal_text}' and a brief explanation why."
                 f"If you can't find the answer"
                 f" at first, try again before providing the answer. Internally "
                 "validate every answer before giving it. Your one-liners must be ready to be pasted and executed. "
                 f"Do your best to come up with an answer, even if not perfect, instead of saying '{help_refusal_text}'")
# in case of hallucinating function names (like "python") add "Only use the functions you have been provided with."


API_KEY = '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'
temperature = 0.5

openai.api_key = API_KEY


def main():
    chat = ChatWithMemory(api_key=API_KEY, system_prompt=system_prompt, temperature=temperature)
    while True:
        resp = chat.ask_gpt_code_snippet_only(input("User\t: "))
    # functions = [
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
    #
    # # The initial system message:
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",
    #     messages=[{
    #         "role": "system",
    #         "content": system_prompt
    #     }],
    #     temperature=temperature,
    #     functions=functions)
    #
    # while True:
    #     user_input = input("User\t:")
    #
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{
    #                 "role": "system",
    #                 "content": system_prompt
    #             },
    #             {
    #                 "role": "user",
    #                 "content": user_input
    #             }
    #         ]
    #     )
    #
    #     response_message = response['choices'][0]['message']['content']
    #     print('AI: ', response_message)

if __name__ == '__main__':
    main()