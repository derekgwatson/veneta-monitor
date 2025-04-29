from ftplib import error_perm


def recursive_list_files(ftp, path):
    file_list = []
    original_path = ftp.pwd()
    ftp.cwd(path)
    items = ftp.nlst()

    for item in items:
        item_path = f"{path}/{item}".replace('//', '/')

        try:
            ftp.cwd(item_path)
            file_list.extend(recursive_list_files(ftp, item_path))  # ✅ pass ftp
            ftp.cwd('..')  # go back
        except error_perm:
            if item.lower().endswith('.xml'):
                file_list.append(item_path)

    ftp.cwd(original_path)  # Go back to starting folder
    return file_list
