python3 -m venv .venv;
.venv/bin/pip install -r requirements.txt;

# Define the full path to python based on the current working directory
PYTHON_PATH="$(pwd)/.venv/bin/python"
CLI_GEN_PATH="$(pwd)/cli-gen.py"

# Get the current shell
current_shell=$(basename "$SHELL");
echo "Current shell: $current_shell";
echo "Python path: $PYTHON_PATH";
echo "cli-gen path: $CLI_GEN_PATH";


# Check if it's zsh
if [ "$current_shell" = "zsh" ]; then
  if grep -q "alias cli-gen=" ~/.zshrc; then
      echo "Alias cli-gen already exists in ~/.zshrc"
  else
      echo "alias cli-gen=\"$PYTHON_PATH $CLI_GEN_PATH\"" >> ~/.zshrc
  fi

# Check if it's bash
elif [ "$current_shell" = "bash" ]; then
  if grep -q "alias cli-gen=" ~/.bashrc; then
      echo "Alias cli-gen already exists in ~/.bashrc"
  else
      echo "alias cli-gen=\"$PYTHON_PATH $CLI_GEN_PATH\"" >> ~/.bashrc
  fi

# Check if it's fish
elif [ "$current_shell" = "fish" ]; then
  if grep -q "function cli-gen" ~/.config/fish/config.fish; then
      echo "Function cli-gen already exists in ~/.config/fish/config.fish"
  else
      echo 'function cli-gen' >> ~/.config/fish/config.fish
      echo "    $PYTHON_PATH $CLI_GEN_PATH \$argv" >> ~/.config/fish/config.fish
      echo 'end' >> ~/.config/fish/config.fish
      echo 'funcsave cli-gen' >> ~/.config/fish/config.fish
  fi
else
    echo "Unsupported shell: $current_shell"
fi
echo "Restart your terminal and then just use 'cli-gen your query'"