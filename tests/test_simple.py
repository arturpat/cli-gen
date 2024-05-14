def test_ls(chat):
    command = chat.ask_gpt_code_snippet_only(
        "list files in directory in the most simple way"
    )
    assert command == "ls"


def test_rm(chat):
    command = chat.ask_gpt_code_snippet_only("remove file named test.txt")
    assert command == "rm test.txt"
