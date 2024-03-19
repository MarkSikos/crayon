
#******************* PASSWORD HANDLING *******************
import bcrypt

def hash_password(plain_text_password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password

def check_password(stored_password, provided_password):
    # provided_password should be a string and will be encoded inside this function
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)
