

def restrict_access(func):
    def wrapper(*args, **kwargs):
        name = args[0]
        if name.startswith("B"):
            return "Access Denied"
        else:
            result = func(*args, **kwargs)
        return result
    return wrapper

@restrict_access
def treasurebox(username):
    return f"Granted Access to {username}"

@restrict_access
def bank_sage(username):
    return f"Granded Access to rich bank safe to {username}"





if __name__ == '__main__':
    print(treasurebox("Anna"))
    print(bank_sage("Bara"))