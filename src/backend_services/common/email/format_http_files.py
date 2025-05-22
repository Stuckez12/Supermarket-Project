'''

'''

def format_html_template(file_path, format_file):
    '''
    
    '''

    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    for placeholder, value in format_file.items():
        html_content = html_content.replace(str(placeholder), str(value))

    return html_content
