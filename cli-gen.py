import os
import re


def ai_function_check_if_file_exists(file_path: str):
    return str(os.path.exists(file_path))


def extract_code_snipped(gpt_answer: str) -> str:
    re_pattern = r"```.*\n(.*)\n```"
    finds = re.findall(re_pattern, gpt_answer)
    if not finds:
        print(gpt_answer)
        raise ValueError("No code found")
    assert len(finds) == 1, "More than one code snipped found, bad bad GPT"
    return finds[0]


system_prompt = ("You are a terminal one-liner generator. Always encapsulate generated code with ```. Answer with "
                 "either the one-liner or with 'I don't know how to help with that'. If you can't find the answer"
                 " at first, try again. Don't be afraid to say 'I don't know how to help with that'. Internally "
                 "validate every answer before giving it. Your one-liners must be ready to be pasted and executed.")
