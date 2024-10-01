import getpass
from bs4 import BeautifulSoup

def wikimedia_login(session, login_url, max_attempts=3):
    for attempt in range(max_attempts):
        print(f"Wikimedia login required. Attempt {attempt + 1}/{max_attempts}")
        username = input("Enter your Wikimedia username: ")
        password = getpass.getpass("Enter your Wikimedia password: ")

        # Get the login page to retrieve the login token
        response = session.get(login_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        login_token = soup.find('input', {'name': 'wpLoginToken'})['value']
        
        login_data = {
            'wpName': username,
            'wpPassword': password,
            'wploginattempt': 'Log in',
            'wpEditToken': '+\\',
            'wpLoginToken': login_token,
            'authAction': 'login',
            'force': '',
        }
        
        # Perform the login
        response = session.post(login_url, data=login_data)
        
        # Check if login was successful
        if 'Log out' in response.text:
            print(f"Login successful for user: {username}")
            return True
        else:
            print(f"Login failed for user: {username}")
            
            # Try to find error messages
            error_msg = soup.find('div', class_='errorbox')
            if error_msg:
                print(f"Error message: {error_msg.text.strip()}")
            else:
                print("No specific error message found. Please check your credentials.")
            
            if attempt < max_attempts - 1:
                print("Retrying...")
            else:
                print("Max login attempts reached. Login failed.")
    
    return False

# You can remove the detect_wikimedia_login function if it's no longer needed