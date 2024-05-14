import sys

import openai

from config import system_prompt, temperature
from utils import ChatWithMemory, get_api_key

# in case of hallucinating function names (like "python") add "Only use the functions you have been provided with."


decisions = {
    "yes": {"yes", "y", "ye", ""},
    "no": {"no", "n"},
    "fresh_start": {"f", "fr", "fresh"},
    "quit": {"q", "Q", "quit"},
    "history": {"h", "hist", "history"},
    "new": {"n", "new"},
    "retry": {"r", "retry"},
}


def main():
    get_api_key()
    chat = ChatWithMemory(system_prompt=system_prompt, temperature=temperature)
    prompt = " ".join(sys.argv[1:])
    try:
        command = chat.ask_gpt_code_snippet_only(prompt)
    except openai.AuthenticationError as e:
        print(f"Incorrect API key provided. Error from OpenAI: {e.error}")
        quit(1)
    while True:
        choice = input(
            "Execute? (Y)es/(R)etry/(N)ew prompt within the same conversation/(Q)uit "
        ).lower()
        if choice in decisions["yes"]:
            chat.execute(command)
            break
        elif choice in decisions["new"]:
            prompt = input("Enter new prompt: ")
            command = chat.ask_gpt_code_snippet_only(prompt)
            continue
        elif choice in decisions["retry"]:
            command = chat.ask_gpt_code_snippet_only(prompt)
            continue
        elif choice in decisions["quit"]:
            break
        else:
            sys.stdout.write("Provide a proper response...")


if __name__ == "__main__":
    main()

# TODO: clean up
# TODO: add tracking history
# TODO: add pretty colors
