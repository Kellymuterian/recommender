import streamlit as st
import mysql.connector
from auth import login_form


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="recommender"
)


def app():
    if not st.session_state.get("authenticated"):
        login_form(conn)
    else:
        st.title(f"Welcome, {st.session_state['username']}!")
        st.write("You are now logged in.")

if __name__ == "__main__":
    app()
