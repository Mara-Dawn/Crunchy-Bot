#!/usr/bin/env sh

files=$(git diff --cached --name-only --diff-filter=AM)

if [ -n "$files" ]; then
    if grep -H TODO $files; then
        echo "Blocking commit as TODO was found."
        exit 1
    fi
fi