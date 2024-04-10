import os
def insert_radios(filename, new_lines, line_numbers):
    """
    This function inserts new lines at specified line numbers in a file.

    Args:
        filename: The name of the file to modify.
        new_lines: A list of strings containing the new lines to insert.
        line_numbers: A list of integers indicating the line numbers for insertion.
    """

    with open(filename, 'r') as file:
        original_lines = file.readlines()

    modified_lines = []
    index = 0
    for i, line in enumerate(original_lines):
        modified_lines.append(line)
        if i + 1 in line_numbers:
            for lines_n in new_lines:
                 modified_lines.append(lines_n+"\n")

    with open(filename, 'w') as file:
        file.writelines(modified_lines)

    os.system('sudo systemctl reload icecast2.service')



def delete_radio_by_name(filename, name):
    """
    This function inserts new lines at specified line numbers in a file.

    Args:
        filename: The name of the file to modify.
        new_lines: A list of strings containing the new lines to insert.
        line_numbers: A list of integers indicating the line numbers for insertion.
    """

    with open(filename, 'r') as file:
        original_lines = file.readlines()

    modified_lines = []
    found_lines = False
    aux = 0
    for i, line in enumerate(original_lines):
        if name+"<" in line:
           removed = modified_lines.pop()
           found_lines = True
           #Se debe ver como se arman los mount-points para definir el siguiente parametro
           aux = 4
           log_delete="<!-- Se borro la radio:" + name +"\n"
           modified_lines.append(log_delete)
           modified_lines.append("-->"+"\n")
        if not aux:
           modified_lines.append(line)
        if aux:
           aux = aux-1

    with open(filename, 'w') as file:
        file.writelines(modified_lines)

    os.system('sudo systemctl reload icecast2.service')
