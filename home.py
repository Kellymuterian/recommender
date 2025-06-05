import streamlit as st
import auth
import mysql.connector
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from itertools import cycle
from PIL import Image
import requests
from io import BytesIO

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
def recommend_items(user_id, top_n=36):
    # Connect to MySQL database
    conn = init_connection()
    cursor = conn.cursor()

    # Read data from MySQL tables
    reviews_query = f"SELECT user_id, product_id, rating FROM reviews"
    cursor.execute(reviews_query)
    reviews_data = cursor.fetchall()

    # Create DataFrames from the fetched data
    reviews_df = pd.DataFrame(reviews_data, columns=['user_id', 'product_id', 'rating'])

    # Aggregate duplicate entries
    reviews_df = reviews_df.groupby(['user_id', 'product_id']).agg({'rating': 'mean'}).reset_index()

    # Create a user-item matrix
    user_item_matrix = reviews_df.pivot(index='user_id', columns='product_id', values='rating').fillna(0)

    # Calculate item-item similarity matrix
    item_similarity_matrix = cosine_similarity(user_item_matrix.T)

    # Create a DataFrame from the similarity matrix
    item_similarity_df = pd.DataFrame(item_similarity_matrix, index=user_item_matrix.columns, columns=user_item_matrix.columns)

    # Fetch user's preferences if available
    preferences_query = f"SELECT category FROM preferences WHERE user_id = {user_id}"
    cursor.execute(preferences_query)
    user_preferences = cursor.fetchall()

    # Convert preferences to a list
    user_preferences = [pref[0] for pref in user_preferences]

    if not user_preferences:
        # User has no preferences
        if user_id not in user_item_matrix.index or user_item_matrix.loc[user_id].sum() == 0:
            # User has no ratings
            # Recommend popular items or items with high average ratings
            popular_items = reviews_df['product_id'].value_counts().index[:top_n]
            return popular_items
        else:
            # User has ratings but no preferences
            user_items = user_item_matrix.loc[user_id]
            # Calculate the weighted sum of item similarities based on user ratings
            weighted_sum = item_similarity_df.mul(user_items, axis=0).sum(axis=1)
            # Sort by weighted sum and recommend top N items
            recommendations = weighted_sum.sort_values(ascending=False).head(top_n)
            return recommendations.index.tolist()
    else:
        # User has preferences
        user_items = user_item_matrix.loc[user_id] if user_id in user_item_matrix.index else pd.Series(0, index=user_item_matrix.columns)

        # Fetch products corresponding to user preferences
        pref_products_query = f"SELECT DISTINCT product_id FROM products WHERE category IN ({', '.join(['%s']*len(user_preferences))})"
        cursor.execute(pref_products_query, user_preferences)
        pref_products = cursor.fetchall()

        # Convert preferences to a list
        pref_products = [pref[0] for pref in pref_products]

        # Filter pref_products to only include indices that are present in user_items
        pref_products_filtered = [prod for prod in pref_products if prod in user_items.index]

        # Set the filtered pref_products to 1 in user_items
        user_items[pref_products_filtered] = 1

        # Calculate the weighted sum of item similarities considering user's ratings and preferences
        weighted_sum = item_similarity_df.mul(user_items, axis=0).sum(axis=1)

        # Sort by weighted sum and recommend top N items
        recommendations = weighted_sum.sort_values(ascending=False).head(top_n)
        return recommendations.index.tolist()


def main(): 
    
    # Placeholder background image URL
    background_image_url = "https://via.placeholder.com/1920x1080"  # Placeholder image URL

    # Update the background image URL with the actual image URL
    background_image_url = "https://i.ibb.co/BtJPmGJ/luxa-org-opacity-changed-original.jpg"

    background_image = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("{background_image_url}");
        background-size: 100vw 100vh;
        background-position: center;  
        background-repeat: no-repeat;
    }}
    
    [data-testid="stVerticalBlock"] {{
        background-color: rgba(255, 255, 255); 
        color: black;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0.1);
        color: black; /* Set the title color to black */
    }}
    
    [data-testid="StyledLinkIconContainer"] {{
       
        color: black;   
    }}

        
    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(0,0,0,0.9);
    }}

    </style>
    """

    st.markdown(background_image, unsafe_allow_html=True)
    conn = init_connection()
    if "authenticated" in st.session_state and st.session_state["authenticated"]:

        with st.container():
            username, user_id = auth.get_user_info(conn)
            st.markdown("""
            <h1 style='text-align: center;color: white'>TOP RECOMMENDATIONS FOR YOU</h1>
            """, unsafe_allow_html=True)
            st.markdown("<hr style='border-top: 2px solid #333; width:100%;'>", unsafe_allow_html=True)

        with st.container():
            recommendations = recommend_items(user_id)

            if len(recommendations) > 0:
                if len(recommendations) >= 10:
                    columns = st.columns(3)
                    for product_id, column in zip(recommendations[:48], cycle(columns)):
                        # Fetch product information from the database based on product_id
                        product_info_query = f"SELECT product_name, store_name, price, product_link, image_url FROM products WHERE product_id = '{product_id}'"
                        cursor = conn.cursor()
                        cursor.execute(product_info_query)
                        product_name, store_name, price, product_link, image_url = cursor.fetchone()

                        # Fetch average rating and number of ratings for the product
                        rating_query = f"SELECT AVG(rating), COUNT(rating) FROM reviews WHERE product_id = '{product_id}'"
                        cursor.execute(rating_query)
                        avg_rating, num_ratings = cursor.fetchone()

                        # Truncate product name if too long
                        max_chars = 25
                        truncated_product_name = product_name[:max_chars] + "..." if len(product_name) > max_chars else product_name

                        # Display the product information in a card-like layout with equal sizes
                        with column:
                            # Replace GIF image URLs with the default image URL
                            image_src = image_url if image_url and not image_url.endswith('.gif') else "https://cleanshelf.s3.eu-central-003.backblazeb2.com/product-images/default.jpg"
                            st.write(
                                f"""
                                <style>
                                .product-card {{
                                    border: 1px solid #ccc;
                                    border-radius: 15px;
                                    padding: 10px;
                                    margin-bottom: 30px;
                                    height: 450px;
                                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    display: flex;
                                    flex-direction: column;
                                    justify-content: space-between;
                                    background-color: #ffff;
                                }}
                                .product-card img {{
                                    width: 100%;
                                    height: 150px;
                                    object-fit: cover;
                                    border-radius: 10px;
                                }}
                                .product-card-details {{
                                    padding: 10px;
                                }}
                                .product-card-details p {{
                                    margin: 5px 0;
                                }}
                                .product-card-details a {{
                                    text-decoration: none;
                                    color: #333;
                                }}
                                .product-card-details button {{
                                    padding: 5px 10px;
                                    background-color: #4CAF50;
                                    color: white;
                                    border: none;
                                    border-radius: 5px;
                                    cursor: pointer;
                                }}
                                </style>
                                <div class="product-card">
                                    <img src="{image_src}" alt="Product Image">
                                    <div class="product-card-details">
                                        <h3>{truncated_product_name}</h3>
                                        <p><strong>Store:</strong> {store_name}</p>
                                        <p><strong>Price:</strong> Ksh {price}</p>
                                        <p><strong>Rating:</strong> {stars_from_rating(avg_rating, num_ratings)}</p>
                                        <a href="{product_link}" target="_blank"><button>View Product</button></a>
                                    </div>
                                </div>
                                """
                                , unsafe_allow_html=True
                            )




                else:
                    st.write("Not enough recommendations available.")
            else:
                st.write("Not enough recommendations available.")


if __name__ == "__main__":
    main()
