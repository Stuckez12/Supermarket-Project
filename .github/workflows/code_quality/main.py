import os

directory = "/path/to/your/folder"


def check_all_files():
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                print(f"Data from {filename}:\n{data}\n{'-'*40}")



if __name__ == "__main__":
    check_all_files()
