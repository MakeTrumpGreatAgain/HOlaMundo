#!/usr/bin/env bash

if [[ ! $- == *i* ]]; then
	>&2 echo "Must be running an interactive terminal"
	>&2 echo "Please use ``source $0'' instead"
	exit 1

fi


# Safe subshell
(
set -ue

# Go to the directory containing the script
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Create the venv if it doesn't exist
if [[ ! -d "venv" ]]; then
	echo "Creating virtual env in venv/ ..."
	virtualenv -p "$( which /usr/bin/python2 )" venv

	echo "Installing python-telegram-bot ..."
	pip install python-telegram-bot
fi

echo "Sourcing venv/bin/activate ..."
source venv/bin/activate

echo "Done!"

)
# End of safe subshell


