# 1. Function ai_function_check_if_exists
#     Check if the file with a given path exists
#       Cast to str (return str(os.path.exists(filename))
#       print if called
# 2. Function strip code. Regex: ```.*\n(.*)\n```. Prints resp and raises value error if not found.
#     catch the value error. This way the answer is printed and the loop continues.
# 3. Prompt:
# "You are a one-liner generator. ... Encapsulate all code with ```. Evaluate first... If can't find try again. Say I don't know.
# 4. Function - straight from api docs
# 5. Spinner -> yaspin (dotsXX)
# 6. Exec: shell_output = subprocess.run(answer, stdout=subprocess.PIPE, shell=True)
#         print(shell_output.stdout.decode("utf-8"))
# 7. Function to decide y/n answer:
import sys


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


# 8. Function:
import os
import platform


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

# 9. include pwd check and adding as a system message
# 10. get new api key
# 11. temperature=0.3

# some inspiration: https://github.com/hunterunger/gpt-cli-assistant/blob/main/main.py
