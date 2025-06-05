import streamlit as st
import mysql.connector
import auth
from styles import background_image_rate
# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommenders"
    )

# Get all products from the database
def get_all_products(conn):
    cursor = conn.cursor()

    query = """
    SELECT product_id, product_name, image_url
    FROM products
    """
    cursor.execute(query)
    products = cursor.fetchall()

    cursor.close()

    return products

# Define the insert_review function
def insert_review(conn, user_id, product_id, rating, review_text):
    cursor = conn.cursor()

    query = """
    INSERT INTO reviews (user_id, product_id, rating, review_text)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, product_id, rating, review_text))
    conn.commit()

    cursor.close()
    
    
# Check if the user has already reviewed the product
def has_user_reviewed(conn, user_id, product_id):
    cursor = conn.cursor()

    query = """
    SELECT COUNT(*)
    FROM reviews
    WHERE user_id = %s AND product_id = %s
    """
    cursor.execute(query, (user_id, product_id))
    count = cursor.fetchone()[0]

    cursor.close()

    return count > 0

# Get the user's existing review for a product
def get_user_review(conn, user_id, product_id):
    cursor = conn.cursor()

    query = """
    SELECT review_text
    FROM reviews
    WHERE user_id = %s AND product_id = %s
    """
    cursor.execute(query, (user_id, product_id))
    review_text = cursor.fetchone()[0]

    cursor.close()

    return review_text

# Update an existing review in the database
def update_review(conn, user_id, product_id, review_text):
    cursor = conn.cursor()

    query = """
    UPDATE reviews
    SET review_text = %s
    WHERE user_id = %s AND product_id = %s
    """
    cursor.execute(query, (review_text, user_id, product_id))
    conn.commit()

    cursor.close()

# Main function
def main():
    conn = init_connection()
    st.markdown(background_image_rate, unsafe_allow_html=True)
    username, user_id = auth.get_user_info(conn)
    
    st.markdown("""
            <h1 style='text-align: center;color: black'>REVIEW PRODUCTS</h1>
            """, unsafe_allow_html=True)
    
    # Extract product ID from the query parameters
    product_id = st.query_params.get('product_id', None)

    if product_id is None:
        # Product ID not provided, display all products for selection
        products = get_all_products(conn)
        search_query = st.text_input("Search for a Product:")
        # Filter products based on search query and user's existing reviews
        filtered_products = [product for product in products if search_query.lower() in product[1].lower()
                             and not has_user_reviewed(conn, user_id, product[0])]

        # Display search results as a grid
        for product_id, product_name, image_url in filtered_products[:10]:  # Display only the first 10 products
            col1, col2 = st.columns([1, 2])
            with col1:
                # Replace GIF image URLs with the default image URL
                image_url = image_url if image_url and not image_url.endswith('.gif') else "https://cleanshelf.s3.eu-central-003.backblazeb2.com/product-images/default.jpg"
                if image_url is not None:  # Check if image_url is not None
                    st.image(image_url, use_column_width=True)
            with col2:
                st.write(product_name)
                
                # Display the review form for each product
                rating = st.slider("Rating:", 1, 5, 3, key=f"rating_{product_id}")
                review_text = st.text_area("Review:", key=f"review_{product_id}")
                if st.button("Submit", key=f"submit_button_{product_id}"):
                    insert_review(conn, user_id, product_id, rating, review_text)
                    st.success("Review submitted successfully!")
            st.markdown("<hr style='border-top: 2px solid #333; width:100%;'>", unsafe_allow_html=True)

    else:
        # Product ID provided, display the review form for the specific product
        product_name = get_product_name_by_id(conn, product_id)
        image_url = get_image_url_by_id(conn, product_id)

        # Display the product information
        st.write(product_name)
        st.image(image_url, use_column_width=True)

        # Display the review form for the product
        rating = st.slider("Rating:", 1, 5, 3, key=f"rating_{product_id}")
        review_text = st.text_area("Review:", key=f"review_{product_id}")
        if st.button("Submit", key=f"submit_button_{product_id}"):
            insert_review(conn, user_id, product_id, rating, review_text)
            st.success("Review submitted successfully!")

    conn.close()



if __name__ == "__main__":
    main()
