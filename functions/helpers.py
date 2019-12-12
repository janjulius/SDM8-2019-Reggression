from cust_logging import print_seperator, log_warning

# Check if statement (lambda) is met, if so prints warning
def check_statement(statement, message, topic):
	if statement():
		print_seperator()
		log_warning(f'{message}\n(CALLBACK FROM: {topic}) ')