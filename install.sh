python3 -m venv .venv;
.venv/bin/pip install -r requirements.txt;

# Define the full path to python based on the current working directory
PYTHON_PATH="$(pwd)/.venv/bin/python"
CLI_GEN_PATH="$(pwd)/cli-gen.py"

# Get the current shell
current_shell=$(basename "$SHELL")

# Check if it's zsh
if [ "$current_shell" == "zsh" ]; then
    echo "alias cli-gen=\"$PYTHON_PATH $CLI_GEN_PATH" >> ~/.zshrc

# Check if it's bash
elif [ "$current_shell" == "bash" ]; then
    echo "alias cli-gen=\"$PYTHON_PATH $CLI_GEN_PATH" >> ~/.bashrc

# Check if it's fish
elif [ "$current_shell" == "fish" ]; then
    echo 'function cli-gen' >> ~/.config/fish/config.fish
    echo "    $PYTHON_PATH ~/path/to/main.py \$argv" >> ~/.config/fish/config.fish
    echo 'end' >> ~/.config/fish/config.fish
    echo 'funcsave cli-gen' >> ~/.config/fish/config.fish
else
    echo "Unsupported shell: $current_shell"
fi