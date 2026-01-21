import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        # bcrypt methods expect bytes
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False # Invalid hash format

def get_password_hash(password: str) -> str:
    # hashpw returns bytes, so we decode to utf-8 string for storage
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
