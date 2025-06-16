'''
This file holds the functions that format all incomming
http files to include the necessary filler information
'''

def format_html_template(file_path: str, format_file: dict) -> str:
    '''
    Receives the file location and data to replace with.

    file_path (str): the location to the html file
    format_file (dict): the data located in the html file to replace

    return (str): html content as a string
    '''

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    for placeholder, value in format_file.items():
        html_content = html_content.replace(str(placeholder), str(value))

    return html_content
