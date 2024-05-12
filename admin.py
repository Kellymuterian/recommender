import streamlit as st
import mysql.connector

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="recommenders"
    )

# Function to add a product to the database
def add_product(conn, product_name, price, store_name, image_url, product_link, category):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO products (product_name, price, currency, store_name, image_url, product_link, category)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    # Set currency to "KES"
    currency = "KES"
    cursor.execute(insert_query, (product_name, price, currency, store_name, image_url, product_link, category))
    conn.commit()
    cursor.close()

# Streamlit app
def main():
    st.title("Admin Panel - Add Product")
    conn = init_connection()

    # Add product form
    with st.form("add_product_form"):
        product_name = st.text_input("Product Name")
        price = st.number_input("Price")
        store_name = st.text_input("Store Name")
        image_url = st.text_input("Image URL")
        product_link = st.text_input("Product Link")
        category = st.text_input("Category")

        submit_button = st.form_submit_button("Add Product")

        if submit_button:
            add_product(conn, product_name, price, store_name, image_url, product_link, category)
            st.success("Product added successfully!")

    conn.close()

if __name__ == "__main__":
    main()
