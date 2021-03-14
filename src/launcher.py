"""This script is the entrypoint of a bot container.
It will import and create a new instance of the class you give it as first argument.

Exemple: python3 ./src/launcher.py TestBot
Will import and launch the TestBot class.
"""

import importlib
import sys

if (len(sys.argv) != 2):
	print("❌ Error: this script should be called with a bot class name")
	print("Exemple: python3 ./src/launcher.py TestBot")
	exit(1)

try:
	module = importlib.import_module(sys.argv[1])
	bot_class = getattr(module, sys.argv[1])
except:
	print(f"❌ Error: cannot find bot with class {sys.argv[1]}")
	print("Make sure your have a class {sys.argv[1]} in a file called {sys.argv[1]}.py in the src directory")
	exit(1)

bot_class()