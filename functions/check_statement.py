from cust_logging import print_seperator

def check_statement(statement, message, topic):
    if statement():
        print_seperator()
        log_warning(f'{message}\n(CALLBACK FROM: {topic}) ')