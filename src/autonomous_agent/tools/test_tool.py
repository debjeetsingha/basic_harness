import os

def get_current_directory():
    """
    Get the current working directory
    """
    cwd = os.getcwd()
    return {"result" : "success", "current_dir" : cwd}

def get_user_name():
    return "Debjeet Singha"