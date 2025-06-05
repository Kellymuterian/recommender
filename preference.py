import streamlit as st
import mysql.connector
from styles import background_image_preference
# Function to initialize database connection
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommenders"
    )

# Function to fetch categories from the products table
def get_categories(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [category[0] for category in cursor.fetchall()]
    cursor.close()
    return categories

# Function to fetch user ID based on username
def get_user_id(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id

# Function to fetch user's preferences
def get_user_preferences(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM preferences WHERE user_id = %s", (user_id,))
    preferences = [preference[0] for preference in cursor.fetchall()]
    cursor.close()
    return preferences

# Function to save user's preferences
def save_user_preferences(conn, user_id, preferences):
    cursor = conn.cursor()
    # Delete existing preferences
    cursor.execute("DELETE FROM preferences WHERE user_id = %s", (user_id,))
    # Insert new preferences
    for preference in preferences:
        cursor.execute("INSERT INTO preferences (user_id, category) VALUES (%s, %s)", (user_id, preference))
    conn.commit()
    cursor.close()

# Function to display preference page
def preference_page(conn):
    st.markdown("""
            <h1 style='text-align: center;color: black'>MANAGE PREFERENCES</h1>
            """, unsafe_allow_html=True)
    
    # Fetch categories from the products table
    categories = get_categories(conn)
    
    # Fetch user ID of the authenticated user
    user_id = st.session_state.get("user_id")
    
    # Fetch user's current preferences
    current_preferences = get_user_preferences(conn, user_id)
    
    # Display user's current preferences
    st.subheader("Your Current Preferences")
    col1, col2, col3 = st.columns(3)
    for i, category in enumerate(categories):
        selected = category in current_preferences
        if i % 3 == 0:
            col = col1
        elif i % 3 == 1:
            col = col2
        else:
            col = col3
        if col.checkbox(category, value=selected, key=category):
            if category not in current_preferences:
                current_preferences.append(category)
        else:
            if category in current_preferences:
                current_preferences.remove(category)
    
    # Allow user to save preferences
    if st.button("Save Preferences"):
        save_user_preferences(conn, user_id, current_preferences)
        st.write("Preferences saved successfully!")
    
    # Display updated preferences
    updated_preferences = get_user_preferences(conn, user_id)
    if updated_preferences:
        st.subheader("Your Preference(s)")
        for category in updated_preferences:
            st.write("✅ " + category)  # Display a checkmark emoji for each preference

# Main function
def main():
    conn = init_connection()
    st.markdown(background_image_preference, unsafe_allow_html=True)
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        preference_page(conn)
    else:
        st.write("Please log in to manage your preferences.")
    
    conn.close()

if __name__ == "__main__":
    main()
