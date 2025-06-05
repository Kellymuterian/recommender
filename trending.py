import streamlit as st
import mysql.connector
import pandas as pd
from itertools import cycle
from styles import background_image

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommenders"
    )

def stars_from_rating(avg_rating, num_ratings):
    if avg_rating is None or num_ratings == 0:
        return "☆☆☆☆☆ (0)"
    else:
        full_stars = int(avg_rating)
        empty_star = "☆"
        colored_star = "<span style='color:gold;'>★</span>"
        empty_colored_star = "<span style='color:grey;'>☆</span>"
        return colored_star * full_stars + empty_colored_star * (5 - full_stars) + f" ({num_ratings})"

def get_popular_items(conn, top_n=45, min_num_reviews=1):
    cursor = conn.cursor()

    # Read data from MySQL tables
    reviews_query = f"SELECT product_id, AVG(rating) AS avg_rating, COUNT(rating) AS num_ratings FROM reviews GROUP BY product_id HAVING num_ratings >= {min_num_reviews}"
    cursor.execute(reviews_query)
    reviews_data = cursor.fetchall()

    # Create DataFrame from the fetched data
    reviews_df = pd.DataFrame(reviews_data, columns=['product_id', 'avg_rating', 'num_ratings'])

    # Get popular items based on number of reviews
    popular_items = reviews_df.sort_values(by=['num_ratings', 'avg_rating'], ascending=False)['product_id'][:top_n]
    
    return popular_items

def main():
    conn = init_connection()
    st.markdown(background_image, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
            <h1 style='text-align: center;color: white'>POPULAR PRODUCTS</h1>
            """, unsafe_allow_html=True)

    with st.container():
        left_column, centre_column, right_column = st.columns(3)    
        popular_items = get_popular_items(conn)

        if len(popular_items) > 0:
            if len(popular_items) >= 36:
                for product_id, column in zip(popular_items[:21], cycle([left_column, centre_column, right_column])):
                    # Fetch product information from the database based on product_id
                    product_info_query = f"SELECT product_name, store_name, price, image_url FROM products WHERE product_id = '{product_id}'"
                    cursor = conn.cursor()
                    cursor.execute(product_info_query)
                    product_name, store_name, price, image_url = cursor.fetchone()

                    # Fetch average rating and number of ratings for the product
                    rating_query = f"SELECT AVG(rating), COUNT(rating) FROM reviews WHERE product_id = '{product_id}'"
                    cursor.execute(rating_query)
                    avg_rating, num_ratings = cursor.fetchone()

                    # Truncate product name if too long
                    max_chars = 30
                    truncated_product_name = product_name[:max_chars] + "..." if len(product_name) > max_chars else product_name

                    # Display the product information in a card-like layout with equal sizes
                    with column:
                        st.write(
                            f"""
                            <div style="background-color: white; color: black; border: 1px solid #eaeaea; border-radius: 5px; padding: 10px; margin-bottom: 10px; height: 450px;">
                                <img src="{image_url}" style="width: 200px; border-radius: 5px; height: 200px; object-fit: cover;">
                                <h3 style="font-weight: bold;">{truncated_product_name}</h3>
                                <p><strong>Store:</strong> {store_name}</p>
                                <p><strong>Price:</strong> {price}</p>
                                <p><strong>Rating:</strong> {stars_from_rating(avg_rating, num_ratings)}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.write("Not enough popular items available.")
        else:
            st.write("Not enough popular items available.")

if __name__ == "__main__":
    main()
