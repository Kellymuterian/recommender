import streamlit as st
import mysql.connector
from mysql.connector import IntegrityError
from mysql.connector.errors import ProgrammingError


# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommender"
    )

def login_success(message, username):
    st.success(message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    st.experimental_set_query_params(authenticated=True)



def login_form(conn,
    title: str = "Authentication",
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    create_title: str = "Create new account :baby: ",
    login_title: str = "Login to existing account :prince: ",
    allow_guest: bool = True,
    guest_title: str = "Guest login :ninja: ",
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
    guest_submit_label: str = "Guest login",
):
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = None

    with st.expander(title, expanded=not st.session_state.get("authenticated", False)):
        # tabs = st.tabs([login_title,create_title ])
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
                        query = f"SELECT * FROM {user_tablename} WHERE {username_col} = '{username}' AND {password_col} = '{password}'"
                        cursor.execute(query)
                        data = cursor.fetchall()
                    except Exception as e:
                        st.error(str(e))
                    else:
                        if len(data) > 0:
                            st.session_state["authenticated"] = True
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
                        cursor = conn.cursor()
                        query = f"INSERT INTO {user_tablename} ({username_col}, {password_col}) VALUES ('{username}', '{password}')"
                        cursor.execute(query)
                        conn.commit()
                    except Exception as e:
                        st.error(str(e))
                    else:
                        st.success(create_success_message)







