import streamlit as st
import mysql.connector
from auth import get_user_info
from styles import background_image_reviews

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="recommenders"
    )

# Get the reviews for the logged-in user
def get_user_reviews(conn):
    _, user_id = get_user_info(conn)
    cursor = conn.cursor()

    query = """
    SELECT r.review_id, r.product_id, r.rating, r.review_text, p.product_name, p.image_url, p.store_name, p.price
    FROM reviews r
    JOIN products p ON r.product_id = p.product_id
    WHERE r.user_id = %s
    """
    cursor.execute(query, (user_id,))
    reviews = cursor.fetchall()

    cursor.close()
    return reviews


# Delete a review from the database
def delete_review(conn, review_id):
    cursor = conn.cursor()
    query = "DELETE FROM reviews WHERE review_id = %s"
    cursor.execute(query, (review_id,))
    conn.commit()
    cursor.close()
    

# Main function
import streamlit as st
import mysql.connector
from auth import get_user_info
from styles import background_image_reviews

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="recommenders"
    )

# Get the reviews for the logged-in user
def get_user_reviews(conn):
    _, user_id = get_user_info(conn)
    cursor = conn.cursor()

    query = """
    SELECT r.review_id, r.product_id, r.rating, r.review_text, p.product_name, p.image_url, p.store_name, p.price
    FROM reviews r
    JOIN products p ON r.product_id = p.product_id
    WHERE r.user_id = %s
    """
    cursor.execute(query, (user_id,))
    reviews = cursor.fetchall()

    cursor.close()
    return reviews


# Delete a review from the database
def delete_review(conn, review_id):
    cursor = conn.cursor()
    query = "DELETE FROM reviews WHERE review_id = %s"
    cursor.execute(query, (review_id,))
    conn.commit()
    cursor.close()

# Main function
def main():
    conn = init_connection()
    reviews = get_user_reviews(conn)
    st.markdown(background_image_reviews, unsafe_allow_html=True)
    st.markdown("""
    <h1 style='text-align: center;color: white'>YOUR REVIEWS</h1>
    """, unsafe_allow_html=True)
    
    for review_id, product_id, rating, review_text, product_name, image_url, store_name, price in reviews:
        st.markdown(
            f"""
            <div style='
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.8), 0 1px 3px rgba(0, 0, 0, 0.08);
                margin-bottom: 20px;
                display: flex;
                background-color: white;
            '>
                <div style='flex: 1; padding: 10px;'>
                    <img src='{image_url}' style='width:200px;height:200px; object-fit: cover;'>
                </div>
                <div style='flex: 2; padding: 10px;'>
                    <h2 style='margin-top:10px;margin-bottom:5px;color:black'>{product_name}</h2>
                    <p style='margin-bottom:5px;color:black'>Rating: {rating}</p>
                    <p style='margin-bottom:5px;color:black'>Review: {review_text}</p>
                    <p style='margin-bottom:5px;color:black'>Store: {store_name}</p>
                    <p style='margin-bottom:10px;color:black'>Price: Ksh {price}</p>
                </div>
            </div>
            """
        , unsafe_allow_html=True)
        
        if st.button("Delete", key=f"delete_button_{review_id}"):
            delete_review(conn, review_id)
            st.experimental_rerun()

    conn.close()

if __name__ == "__main__":
    main()



