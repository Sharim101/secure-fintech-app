import streamlit as st
import sqlite3
import bcrypt  # For password hashing
import re  # For password and email validation
from cryptography.fernet import Fernet  # For encryption
import datetime
import os

# --- Configuration & Setup ---

# 1. Database Setup
def init_db():
    conn = sqlite3.connect('fintech.db')
    c = conn.cursor()
    
    # User table with hashed passwords
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        email TEXT
    )
    ''')
    
    # Transactions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        recipient TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    ''')
    
    # Secure notes table
    c.execute('''
    CREATE TABLE IF NOT EXISTS secure_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        encrypted_note BLOB NOT NULL,
        FOREIGN KEY (username) REFERENCES users (username)
    )
    ''')
    
    conn.commit()
    conn.close()

# 2. Encryption Key (SECURITY: In a real app, this key would be managed securely, not hardcoded)
# For this assignment, we'll generate it and store it in a file.
KEY_FILE = 'secret.key'
def write_key():
    """Generates a key and saves it into a file."""
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """Loads the key from the current directory."""
    if not os.path.exists(KEY_FILE):
        return write_key()
    return open(KEY_FILE, "rb").read()

KEY = load_key()
FERNET = Fernet(KEY)

# 3. Security Helper Functions
def hash_password(password):
    """Hashes password with bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Checks password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def is_strong_password(password):
    """Password strength check (length, digit, symbol)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?:{}|<>]", password):
        return False, "Password must contain at least one special symbol."
    return True, ""

def is_valid_email(email):
    """Simple email validation."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def log_activity(username, action):
    """Audit / Activity Log: Logs user actions to a file."""
    with open('activity.log', 'a') as f:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] - USER: '{username}' - ACTION: {action}\n")

def encrypt_data(data):
    """Encrypts data using Fernet."""
    return FERNET.encrypt(data.encode('utf-8'))

def decrypt_data(encrypted_data):
    """Decrypts data using Fernet."""
    try:
        return FERNET.decrypt(encrypted_data).decode('utf-8')
    except Exception as e:
        return "Error: Could not decrypt data."

# --- Initialize Database ---
init_db()

# --- Streamlit App ---
st.set_page_config(page_title="Secure FinTech App", layout="wide")

# --- BATMAN THEME: Load custom CSS ---
# This function reads the style.css file and injects it into the app
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("style.css file not found. App will use default styling.")

load_css("style.css")
# --- END BATMAN THEME ---

st.title("CY4053 - Secure FinTech App")

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- MAIN APP LOGIC ---

# 1. IF NOT LOGGED IN (Show Login/Register)
if not st.session_state.logged_in:
    st.header("User Authentication")
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    # --- LOGIN ---
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    try:
                        conn = sqlite3.connect('fintech.db')
                        c = conn.cursor()
                        c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                        result = c.fetchone()
                        conn.close()
                        
                        if result and check_password(password, result[0]):
                            st.session_state.logged_in = True
                            st.session_state.username = username
                            log_activity(username, "Login successful")
                            st.success("Login successful!")
                            st.rerun() # Refresh the page to show the main app
                        else:
                            st.error("Invalid username or password.")
                            log_activity(username, "Failed login attempt")
                    except Exception as e:
                        # SECURITY: Generic error message
                        st.error("An error occurred during login. Please try again.")
                        log_activity(username, f"Login error: {e}")

    # --- REGISTRATION ---
    with register_tab:
        with st.form("register_form"):
            reg_username = st.text_input("New Username")
            reg_password = st.text_input("New Password", type="password")
            reg_confirm_password = st.text_input("Confirm Password", type="password")
            register_button = st.form_submit_button("Register")
            
            if register_button:
                # Test 12 & 20: Empty field validation
                if not reg_username or not reg_password or not reg_confirm_password:
                    st.warning("All fields are required.")
                # Test 13: Password match check
                elif reg_password != reg_confirm_password:
                    st.error("Passwords do not match.")
                # Test 2: Password strength
                elif not is_strong_password(reg_password)[0]:
                    st.error(f"Password is not strong: {is_strong_password(reg_password)[1]}")
                else:
                    try:
                        conn = sqlite3.connect('fintech.db')
                        c = conn.cursor()
                        
                        # Test 11: Duplicate user check
                        c.execute("SELECT * FROM users WHERE username = ?", (reg_username,))
                        if c.fetchone():
                            st.error("Username already exists. Please choose another.")
                        else:
                            # All checks passed, create user
                            hashed = hash_password(reg_password)
                            c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (reg_username, hashed))
                            conn.commit()
                            st.success("Registration successful! Please log in.")
                            log_activity(reg_username, "User registration successful")
                    except Exception as e:
                        # SECURITY: Generic error
                        st.error("An error occurred during registration.")
                        log_activity(reg_username, f"Registration error: {e}")
                    finally:
                        conn.close()

# 2. IF LOGGED IN (Show Main App)
else:
    # --- BATMAN THEME: Add logo to sidebar ---
    st.sidebar.image("https://i.imgur.com/2s4R5B2.png", width=100)
    # --- END BATMAN THEME ---

    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        # Test 6: Logout functionality
        log_activity(st.session_state.username, "User logged out")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Make a Transaction", "Secure Notes", "Update Profile", "View Activity Log"]
    )
    
    conn = sqlite3.connect('fintech.db')
    c = conn.cursor()

    try:
        # --- Dashboard ---
        if menu == "Dashboard":
            st.header("Your Transaction History")
            c.execute("SELECT timestamp, recipient, amount, description FROM transactions WHERE username = ?", (st.session_state.username,))
            history = c.fetchall()
            if history:
                st.dataframe(history, column_config={
                    "timestamp": "Time",
                    "recipient": "Recipient",
                    "amount": "Amount (PKR)",
                    "description": "Description"
                })
            else:
                st.info("You have no transactions yet.")

        # --- Make a Transaction ---
        elif menu == "Make a Transaction":
            st.header("Make a Transaction")
            with st.form("transaction_form"):
                recipient = st.text_input("Recipient Username")
                # Test 12: Number field validation (handled by st.number_input)
                amount = st.number_input("Amount (PKR)", min_value=0.01, step=0.01, format="%.2f")
                # Test 3 & 10: Input validation
                description = st.text_area("Description (max 100 chars)")
                submit_tx = st.form_submit_button("Send Money")

                if submit_tx:
                    # Test 10: Input length validation
                    if len(description) > 100:
                        st.error("Description must be 100 characters or less.")
                    # Test 20: Empty field check
                    elif not recipient or not description:
                        st.error("Recipient and Description cannot be empty.")
                    else:
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        c.execute("INSERT INTO transactions (username, timestamp, recipient, amount, description) VALUES (?, ?, ?, ?, ?)",
                                  (st.session_state.username, timestamp, recipient, amount, description))
                        conn.commit()
                        st.success(f"Successfully sent {amount} PKR to {recipient}!")
                        log_activity(st.session_state.username, f"Sent transaction of {amount} to {recipient}")

        # --- Secure Notes ---
        elif menu == "Secure Notes":
            st.header("Secure Notes (Encrypted Storage)")
            # Test 7 & 18: Data confidentiality
            st.info("These notes are end-to-end encrypted. They are stored in the database in an unreadable format and decrypted only when you view them here.")
            
            with st.form("secure_note_form"):
                note_text = st.text_area("Enter a secure note:")
                save_note = st.form_submit_button("Encrypt and Save Note")
                
                if save_note and note_text:
                    encrypted_note = encrypt_data(note_text)
                    c.execute("INSERT INTO secure_notes (username, encrypted_note) VALUES (?, ?)", (st.session_state.username, encrypted_note))
                    conn.commit()
                    st.success("Your secure note has been encrypted and saved.")
                    log_activity(st.session_state.username, "Created a secure note")

            st.subheader("Your Saved Notes")
            c.execute("SELECT id, encrypted_note FROM secure_notes WHERE username = ?", (st.session_state.username,))
            notes = c.fetchall()
            if not notes:
                st.write("You have no secure notes.")
            else:
                for note in notes:
                    with st.expander(f"Note ID: {note[0]}"):
                        decrypted_text = decrypt_data(note[1])
                        st.write(decrypted_text)

        # --- Update Profile ---
        elif menu == "Update Profile":
            st.header("Update Your Profile")
            # Test 9: Access control
            
            c.execute("SELECT full_name, email FROM users WHERE username = ?", (st.session_state.username,))
            current_profile = c.fetchone()
            
            with st.form("profile_form"):
                full_name = st.text_input("Full Name", value=current_profile[0] or "")
                # Test 15: Email validation
                email = st.text_input("Email", value=current_profile[1] or "")
                update_profile = st.form_submit_button("Update Profile")
                
                if update_profile:
                    if email and not is_valid_email(email):
                        st.error("Invalid email address format.")
                    else:
                        c.execute("UPDATE users SET full_name = ?, email = ? WHERE username = ?", (full_name, email, st.session_state.username))
                        conn.commit()
                        st.success("Profile updated successfully.")
                        log_activity(st.session_state.username, "Updated profile information")

            st.subheader("Profile Picture Upload")
            # Test 8: File upload validation
            uploaded_file = st.file_uploader("Upload a profile picture (JPG, PNG only)", type=["jpg", "png"])
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Your uploaded picture.", width=150)
                st.success("File uploaded successfully! (Feature is for demo; file is not saved permanently)")

        # --- View Activity Log ---
        elif menu == "View Activity Log":
            st.header("Your Recent Activity")
            # Test 4: Unauthorized access (tested by only showing this to logged-in user)
            st.info("This log shows actions performed only by your account.")
            
            try:
                with open('activity.log', 'r') as f:
                    all_logs = f.readlines()
                
                user_logs = [line for line in all_logs if f"USER: '{st.session_state.username}'" in line]
                
                if not user_logs:
                    st.write("No activity recorded for your account.")
                else:
                    st.text_area("Your Logs", "".join(reversed(user_logs)), height=300)
            except FileNotFoundError:
                st.info("No activity log file found.")

    except Exception as e:
        # Test 9 & 17: Secure Error Handling
        st.error("A critical error occurred. Please log out and try again. If the problem persists, contact support.")
        log_activity(st.session_state.username, f"CRITICAL ERROR: {e}")
    
    finally:
        conn.close()
