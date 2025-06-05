import streamlit as st
import mysql.connector
import re
from mysql.connector import IntegrityError
from mysql.connector.errors import ProgrammingError
import hashlib

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommenders"
    )

def validate_username(username, conn, min_length=3, max_length=20, allowed_chars=r"[a-zA-Z0-9_\-]+", reserved_usernames=None, user_tablename="users", username_col="username"):
    if reserved_usernames is None:
        reserved_usernames = []

    if len(username) < min_length or len(username) > max_length:
        return False

    if not re.match(allowed_chars, username):
        return False

    if sum(1 for char in username if char.isalpha()) < 2:
        return False

    cursor = conn.cursor()
    query = f"SELECT * FROM {user_tablename} WHERE {username_col} = '{username}'"
    cursor.execute(query)
    if cursor.fetchone():
        return False

    return True

def validate_email(email, conn, email_col="email", user_tablename="users"):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email address format."

    cursor = conn.cursor()
    query = f"SELECT * FROM {user_tablename} WHERE {email_col} = '{email}'"
    cursor.execute(query)
    if cursor.fetchone():
        return False, "Email address already exists."
    
    return True, ""

def validate_password(password):
    min_length = 8
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long."
    if not re.search("[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search("[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search("[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.search("[!@#$%^&*()_+=\-{}[\]:\"|<>?,./]", password):
        return False, "Password must contain at least one special character."
    return True, ""

def login_success(login_success_message, username, user_id, is_admin=False):
    st.success(login_success_message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id
    st.session_state["is_admin"] = is_admin
    st.experimental_set_query_params(authenticated=True, username=username)

def is_admin():
    return st.session_state.get("is_admin", False)

def get_user_info(conn):
    if st.session_state["authenticated"]:
        username = st.session_state["username"]
        user_id = st.session_state["user_id"]
        if not user_id:
            cursor = conn.cursor()
            query = f"SELECT user_id FROM users WHERE username = '{username}'"
            cursor.execute(query)
            data = cursor.fetchone()
            if data:
                user_id = data[0]
                st.session_state["user_id"] = user_id
        return username, user_id
    return None, None

def is_authenticated():
    return st.session_state.get("authenticated", False)

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["is_admin"] = False

def login_form(conn):
    st.markdown("""
    <h1 style='text-align: center'>GROCERY🛒GO</h1>
    """, unsafe_allow_html=True)

    if not st.session_state.get("authenticated", False):
        st.session_state["authenticated"] = False

    if not st.session_state.get("username", None):
        st.session_state["username"] = None
        
    background_image_url = "https://i.ibb.co/BtJPmGJ/luxa-org-opacity-changed-original.jpg"

    with st.container():
        
        background_image = f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-image: url("{background_image_url}");
            background-size: 100vw 100vh;
            background-position: center;  
            background-repeat: no-repeat;
        }}
        [data-testid="stVerticalBlock"] {{
        background-color: rgba(255,255,255); 
        color: black;
        }}
        [data-testid="stHeader"] {{
        background: rgba(0,0,0,0.1);
        }}
        </style>
        """
        st.markdown(background_image, unsafe_allow_html=True)
        
        with st.expander("", expanded=not st.session_state.get("authenticated", False)):
            login_tab, create_tab = st.tabs(["Login to existing account :prince:", "Create new account :baby: "])

            with login_tab:
                with st.form(key="login"):
                    username = st.text_input("Enter your unique username")
                    password = st.text_input("Enter your password", type="password")

                    if st.form_submit_button("Login"):
                        if username == "admin" and password == "Admin@123":
                            login_success("Login succeeded :tada:", username, -1, is_admin=True)
                            st.rerun()
                        else:
                            cursor = conn.cursor()
                            query = f"SELECT password FROM users WHERE username = '{username}'"
                            cursor.execute(query)
                            data = cursor.fetchone()
                            if data:
                                hashed_password = data[0]
                                entered_hashed_password = hashlib.sha256(password.encode()).hexdigest()
                                if hashed_password == entered_hashed_password:
                                    user_id_query = f"SELECT user_id FROM users WHERE username = '{username}'"
                                    cursor.execute(user_id_query)
                                    user_id = cursor.fetchone()[0]
                                    login_success("Login succeeded :tada:", username, user_id)
                                    st.rerun()
                                else:
                                    st.error("Wrong username/password :x:")
                            else:
                                st.error("Wrong username/password :x:")

            with create_tab:
                with st.form(key="create"):
                    username = st.text_input("Create a unique username")
                    email = st.text_input("Enter your email")
                    password = st.text_input("Create a password", type="password")

                    if st.form_submit_button("Create account"):
                        if not validate_username(username, conn):
                            st.error("Invalid username.")
                            return
                        is_valid_email, email_error_message = validate_email(email, conn)
                        if not is_valid_email:
                            st.error(email_error_message)
                            return
                        is_valid_password, password_error_message = validate_password(password)
                        if not is_valid_password:
                            st.error(password_error_message)
                            return
                        hashed_password = hashlib.sha256(password.encode()).hexdigest()
                        cursor = conn.cursor()
                        query = f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{hashed_password}')"
                        cursor.execute(query)
                        conn.commit()
                        st.success("Account created :tada:")

