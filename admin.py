import streamlit as st
import mysql.connector
from streamlit_option_menu import option_menu
import auth
import home, trending, search, your_reviews, rate, preference

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="recommenders"
    )

def get_categories(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return categories

def get_category_index(conn, category):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM (SELECT DISTINCT category FROM products WHERE category < %s) AS subquery", (category,))
    index = cursor.fetchone()[0]
    cursor.close()
    return index

def get_product_by_id(conn, product_id):
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM products WHERE product_id = %s"
    cursor.execute(select_query, (product_id,))
    product = cursor.fetchone()
    cursor.close()
    return product

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

# Function to edit a product in the database
def edit_product(conn, product_id, product_name, price, store_name, image_url, product_link, category):
    cursor = conn.cursor()
    update_query = """
    UPDATE products
    SET product_name = %s, price = %s, store_name = %s, image_url = %s, product_link = %s, category = %s
    WHERE product_id = %s
    """
    cursor.execute(update_query, (product_name, price, store_name, image_url, product_link, category, product_id))
    conn.commit()
    cursor.close()

# Function to search for products based on a search query
def search_products(conn, search_query):
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM products WHERE product_name LIKE %s"
    cursor.execute(select_query, (f"%{search_query}%",))
    products = cursor.fetchall()
    cursor.close()
    return products

# Function to delete a product by its ID
def delete_product(conn, product_id):
    cursor = conn.cursor()
    delete_query = """
    DELETE FROM products
    WHERE product_id = %s
    """
    cursor.execute(delete_query, (product_id,))
    conn.commit()
    cursor.close()

# Function to fetch all users from the database
def get_all_users(conn):
    cursor = conn.cursor(dictionary=True)  # This ensures that results are returned as dictionaries
    select_query = """
    SELECT * FROM users
    """
    cursor.execute(select_query)
    users = cursor.fetchall()
    cursor.close()
    return users

# Function to delete user from the database
def delete_user(conn, user_id):
    cursor = conn.cursor()
    delete_query = """
    DELETE FROM users
    WHERE user_id = %s
    """
    cursor.execute(delete_query, (user_id,))
    conn.commit()
    cursor.close()

# Function to show the add product form
def show_add_product_form(conn):
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

# Function to show the edit product form
def show_edit_product_form(conn):
    search_query = st.text_input("Search Product", help="Enter a product name to search")

    if st.button("Search"):
        products = search_products(conn, search_query)

        if products:
            st.write("Search Results:")
            selected_product = st.selectbox("Select a Product", options=products, format_func=lambda x: x['product_name'])

            # Product preview and image upload
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Current Product")
                st.image(selected_product['image_url'])
                st.write(f"Product Name: {selected_product['product_name']}")
                st.write(f"Price: {selected_product['price']} {selected_product['currency']}")
                st.write(f"Store Name: {selected_product['store_name']}")
                st.write(f"Product Link: {selected_product['product_link']}")
                st.write(f"Category: {selected_product['category']}")
            with col2:
                st.subheader("Edit Product")
                product_name = st.text_input("New Product Name", value=selected_product['product_name'])
                price = st.number_input("Price", value=float(selected_product['price']), min_value=0.0)  # Convert Decimal to float and add min_value validation
                store_name = st.text_input("Store Name", value=selected_product['store_name'])
                image_url = st.text_input("Image URL", value=selected_product['image_url'])
                product_link = st.text_input("Product Link", value=selected_product['product_link'])
                categories = get_categories(conn)
                category = st.selectbox("Category", options=categories, index=get_category_index(conn, selected_product['category']))  # Add filtering and sorting options

            # Undo/redo functionality
            undo_button = st.button("Undo")
            redo_button = st.button("Redo")
            if undo_button:
                # Implement undo functionality
                pass
            if redo_button:
                # Implement redo functionality
                pass

            # Save button
            if st.button("Save Changes"):
                # Validate user inputs
                if not product_name or not price or not store_name or not image_url or not product_link or not category:
                    st.error("Please fill in all the required fields.")
                    return
                if not is_valid_price(price):
                    st.error("Please enter a valid price.")
                    return
                if not is_valid_product_link(product_link):
                    st.error("Please enter a valid product link.")
                    return
                if not is_valid_category(category):
                    st.error("Please select a valid category.")
                    return

                # Save the updated product details
                edit_product(conn, selected_product['product_id'], product_name, price, store_name, image_url, product_link, category)
                st.success("Product updated successfully.")
        else:
            st.error("Product not found.")

# Function to show the manage users page
def show_manage_users(conn):
    with st.container():
        st.title("Manage Users")

        # Search box for filtering users
        search_query = st.text_input("Search by Username")

        # Fetch all users or filtered users based on search query
        users = get_all_users(conn)
        if search_query:
            users = [user for user in users if search_query.lower() in user['username'].lower()]

        for user in users:
            st.write(f"Username: {user['username']}, Email: {user['email']}")
            delete_button = st.button(f"Delete {user['username']}")

            if delete_button:
                delete_user(conn, user['user_id'])  # Assuming 'id' is the user's unique identifier in the database
                st.success(f"User {user['username']} deleted successfully!")
                st.rerun()

# Function to show the delete product form
def show_delete_product_form(conn):
    with st.form("delete_product_form"):
        product_id = st.number_input("Product ID")

        submit_button = st.form_submit_button("Delete Product")

        if submit_button:
            delete_product(conn, product_id)
            st.success("Product deleted successfully!")

# Function to show the admin panel
def show_admin_panel(conn):
    menu_title = "Admin Menu"

    class MultiApp:
        def __init__(self, menu_title):
            self.apps = []
            self.menu_title = menu_title

        def add_app(self, title, func):
            self.apps.append({
                "title": title,
                "function": func
            })

        def run(self):
            st.markdown(
                """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """,
                unsafe_allow_html=True
            )

            with st.sidebar:
                app = option_menu(
                    menu_title=menu_title,
                    options=['Add Product', 'Edit Product', 'Manage Users', 'Delete Products', 'Logout'],
                    icons=['bi bi-bag-plus-fill', 'bi bi-pencil-square', 'bi bi-person-circle', 'bi bi-trash-fill','bi bi-box-arrow-right'],
                    default_index=0
                )

            for item in self.apps:
                if app == item['title']:
                    item['function'](conn)
                elif app == "Logout":
                    auth.logout()
                    st.rerun()

    multi_app = MultiApp(menu_title)
    multi_app.add_app('Add Product', show_add_product_form)
    multi_app.add_app('Edit Product', show_edit_product_form)
    multi_app.add_app('Manage Users', show_manage_users)
    multi_app.add_app('Delete Products', show_delete_product_form)

    multi_app.run()

# Streamlit app
def main():
    conn = init_connection()
    show_admin_panel(conn)

    conn.close()

if __name__ == "__main__":
    main()