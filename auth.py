import streamlit as st
import mysql.connector
import re
from mysql.connector import IntegrityError
from mysql.connector.errors import ProgrammingError




# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommenders"
    )

def validate_email(email):
    """Validate the email format."""
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email address format."
    return True, ""

def validate_password(password):
    """Validate the password against requirements."""
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




def login_success(login_success_message, username, user_id):
    st.success(login_success_message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.session_state["user_id"] = user_id
    st.experimental_set_query_params(authenticated=True, username=username)


st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("username", None)
st.session_state.setdefault("user_id", None)

def get_user_info(conn):
    if st.session_state["authenticated"]:
        username = st.session_state["username"]
        user_id = st.session_state["user_id"]
        if not user_id:
            # Fetch user_id from database
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
    authenticated = st.session_state.get("authenticated", False)
    return authenticated

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None



def login_form(
    conn,
    title: str = "GROCERY RECOMMENDER SYSTEM",
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    email_col: str = "email", 
    create_email_label: str = "Enter your email",
    create_email_placeholder: str = None,
    create_email_help: str = None,
    create_title: str = "Create new account :baby: ",
    login_title: str = "Login to existing account :prince: ",
    create_username_label: str = "Create a unique username",
    create_username_placeholder: str = None,
    create_username_help: str = None,
    create_password_label: str = "Create a password",
    create_password_placeholder: str = None,
    create_password_help: str = "⚠️ Password will be stored as plain text. Do not reuse from other websites. Password cannot be recovered.",
    create_submit_label: str = "Create account",
    create_success_message: str = "Account created :tada:",
    login_username_label: str = "Enter your unique username",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Enter your password",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    login_submit_label: str = "Login",
    login_success_message: str = "Login succeeded :tada:",
    login_error_message: str = "Wrong username/password :x: ",
    
):
    st.title(title)
  
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = None
        
    background_image_url = "https://images.unsplash.com/photo-1506617564039-2f3b650b7010?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    
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
        background-color: rgba(0, 0, 0, 0.5); 
        color: white;
        }}
        [data-testid="stHeader"] {{
        background: rgba(0,0,0,0.1);
        }}
        </style>
        """
        st.markdown(background_image, unsafe_allow_html=True)
        
        
        with st.expander("", expanded=not st.session_state.get("authenticated", False)):
            if login_title:
                login_tab, create_tab  = st.tabs(
                    [
                        login_title,
                        create_title,
                        
                    ]
                )
            else:
                login_tab, create_tab = st.tabs(
                    [
                        login_title,
                        create_title,
                        
                    ]
                )



            with login_tab: # Login to existing account tab
                with st.form(key="login"):
                    username = st.text_input(
                        label=login_username_label,
                        placeholder=login_username_placeholder,
                        help=login_username_help,
                        disabled=st.session_state["authenticated"],
                    )

                    password = st.text_input(
                        label=login_password_label,
                        placeholder=login_password_placeholder,
                        help=create_password_help,
                        type="password",
                        disabled=st.session_state["authenticated"],
                    )

                    if st.form_submit_button(
                        label=login_submit_label,
                        disabled=st.session_state["authenticated"],
                        type="primary",
                    ):
                        try:
                            cursor = conn.cursor()
                            query = f"SELECT * FROM {user_tablename} WHERE {username_col} = '{username}'AND {password_col} = '{password}'"
                            cursor.execute(query)
                            data = cursor.fetchall()
                        except Exception as e:
                            st.error(str(e))
                        else:
                            if len(data) > 0:
                                user_id = data[0][0]   # Assuming user_id is a key in the result
                                login_success(login_success_message, username, user_id)
                                st.rerun()

                                
                            else:
                                st.error(login_error_message)       
                                
            with create_tab:  # Create new account tab
                with st.form(key="create"):
                    username = st.text_input(
                        label=create_username_label,
                        placeholder=create_username_placeholder,
                        help=create_username_help,
                        disabled=st.session_state["authenticated"],
                    )
                    
                    email = st.text_input(
                        label=create_email_label,
                        placeholder=create_email_placeholder,
                        help=create_email_help,
                        disabled=st.session_state["authenticated"],
                    )

                    password = st.text_input(
                        label=create_password_label,
                        placeholder=create_password_placeholder,
                        help=create_password_help,
                        type="password",
                        disabled=st.session_state["authenticated"],
                    )
                    

                    if st.form_submit_button(
                        label=create_submit_label,
                        type="primary",
                        disabled=st.session_state["authenticated"],
                    ):
                        try:
                             # Validate email
                            is_valid_email, email_error_message = validate_email(email)
                            if not is_valid_email:
                                st.error(email_error_message)
                                return
                                                       
                            # Validate password
                            is_valid_password, password_error_message = validate_password(password)
                            if not is_valid_password:
                                st.error(password_error_message)
                                return


                            cursor = conn.cursor()
                            query = f"INSERT INTO {user_tablename} ({username_col},{email_col}, {password_col}) VALUES ('{username}','{email}', '{password}')"
                            cursor.execute(query)
                            conn.commit()
                        except Exception as e:
                            st.error(str(e))
                        else:
                            st.success(create_success_message)


                            













