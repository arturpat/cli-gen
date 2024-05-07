import os
import sys

import openai

from utils import ChatWithMemory, help_refusal_text

system_prompt = (
    "You are a terminal one-liner generator. Always encapsulate generated code with ```. Answer with "
    f"either the one-liner or with '{help_refusal_text}' and a brief explanation why."
    f"If you can't find the answer"
    f" at first, try again before providing the answer. Internally "
    "validate every answer before giving it. Your one-liners must be ready to be pasted and executed. "
    f"Do your best to come up with an answer, even if not perfect, instead of saying '{help_refusal_text}'"
)
# in case of hallucinating function names (like "python") add "Only use the functions you have been provided with."


temperature = 0.2

decisions = {
    "yes": {"yes", "y", "ye", ""},
    "no": {"no", "n"},
    "fresh_start": {"f", "fr", "fresh"},
    "quit": {"q", "Q", "quit"},
    "history": {"h", "hist", "history"},
    "new": {"n", "new"},
    "retry": {"r", "retry"},
}


def get_api_key() -> str:
    # check from env vars
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    # check in the file
    current_directory = os.path.dirname(
        os.path.abspath(__file__)
    )  # cli-gen.py location
    try:
        with open(
            os.path.join(current_directory, "open_ai_api_key.txt")
        ) as api_key_file:
            key = api_key_file.readlines()[0].strip("\n")
            os.environ["OPENAI_API_KEY"] = key
            return key
    except FileNotFoundError:
        pass  # no file with expected name
    except IndexError:
        pass  # empty file

    # not found in file, not found in env vars
    print("API key not found in env vars (searched for OPENAI_API_KEY) or in a file.")
    print(
        "Go to Go to https://platform.openai.com/api-keys to generate one for yourself"
    )
    print("OpenAI offers a free $5 worth credits for everyone once.")
    print(
        "Either paste the key here to store it next to cli-gen.py or save it as OPENAI_API_KEY yourself."
    )
    key = input("Key: ")
    # set up the key for now
    os.environ["OPENAI_API_KEY"] = key

    # dump the key

    with open(os.path.join(current_directory, "open_ai_api_key.txt"), "w") as text_file:
        print(key, file=text_file)
    print(
        f"Thanks, api key saved at {os.path.join(current_directory, 'open_ai_api_key.txt')}\n"
    )

    return key
    # if not present, either ask to fill in or link to openai api tokens


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
# TODO: add asking for openai api key
