from datetime import datetime
import sys

try: color = sys.stdout.shell
except AttributeError: raise RuntimeError("Use IDLE")

def log_error(message):
    color.write(f'ERROR: {message}\n', "COMMENT");

def log_message(message):
    color.write(f'OK: {message}\n', "STRING");

def log_warning(message):
    color.write(f'WARN: {message}\n', "KEYWORD");
	
def print_seperator():
    color.write("\n#############################################\n\n", "KEYWORD")
    print(f"{datetime.now()}")