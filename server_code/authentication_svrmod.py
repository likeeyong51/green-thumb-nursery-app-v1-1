import anvil.files
from anvil.files import data_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import bcrypt

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
@anvil.server.callable
def get_user_roles():
    '''return all roles from the role table'''
    return app_tables.role.search()

@anvil.server.callable
def signup_user(firstname, lastname, emp_id, role, password):
    '''Signs up a new user, ensuring the username is unique.'''
    username = firstname.replace(' ', '').lower() # remove spaces
    email = f"{username}@nursery.com"

    # check if a user with this first name already exists
    if app_tables.users.get(email=email) and verify_password(password.encode('utf-8'), get_hashed_password(email)):
        # create a more unique username
        username = f"{firstname.replace(' ', '').lower()}{lastname.replace(' ', '').lower()}"
        email = f"{username}@nursery.com"

        # check again with the combined name
        if app_tables.users.get(email=email) and verify_password(password.encode('utf-8'), get_hashed_password(email)):
            print(f"User {username} already exists.")
            # raise anvil.server.ExecutionTerminatedError("A user with this name already exists.")
            return False, username

    # if username is unique, create the user account
    new_user = app_tables.users.add_row(
        email=email,
        enabled=True,
        password_hash=hash_password(password).decode('utf-8'), # store hash password as text
        # confirmed_email=True,
        role=role)

    return new_user, username

@anvil.server.callable
def get_user_role(email):
    '''return user role based on username'''
    user = app_tables.users.get(email=email)

    if user: # if user exists
        return user['role']
        
#--------------------
# utility functions
#--------------------

def get_hashed_password(email):
    '''get the hash_password for verification'''
    # get user info based on login email
    user = app_tables.users.get(email=email)

    if user: # if found
        return user['password_hash'].encode('utf-8')

    return None

def hash_password(password):
    '''encrypt and returned a hashed password'''
    # Generate a salt
    salt = bcrypt.gensalt()
    # Create a hash
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    # print(hashed_password.decode('utf-8'))
    return hashed_password

def verify_password(password, hashed_password):
    '''verify the password entered is the same as the one stored in the user record'''
    # Check if the password matches the hash
    # print(f'{password = }')
    # print(f'{hashed_password = }')
    return bcrypt.checkpw(password, hashed_password)

# originally implemented, but will use the one from the builtin service
# @anvil.server.callable
# def signin_user(username, password):
#     '''login verification and setting access based on role'''
#     if not username and not password:
#         return False, None # invalid password; login failed
        
#     # build email string
#     email = f'{username}@nursery.com'

#     # check if a user with this username exists and password matches
#     if app_tables.users.get(email=email) and verify_password(password.encode('utf-8'), get_hashed_password(email)):
#         return True, get_user_role(email) # login sucessful

#     return False, None

