#!/bin/bash

# Loop through all files in .cmds folder
for script in .cmds/*; do
    # Check if the file is executable and is a regular file
    if [ -x "$script" ] && [ -f "$script" ]; then
        echo "Running $script"
        # Source the script to run it in the current shell
        source "$script"
    fi
done