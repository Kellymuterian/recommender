import streamlit as st
import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from fuzzywuzzy import process
from difflib import SequenceMatcher
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from styles import background_image_search

# Download NLTK data (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')

search_history = []

# Function to load data from MySQL database
def load_data():
    try:
        # Database connection details
        host = 'localhost'
        user = 'root'
        password = ''
        database = 'recommenders'

        # Create a SQLAlchemy engine
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

        # Connect to the database
        conn = engine.connect()

        # Query to load data
        query = """
        SELECT p.product_id, p.product_name, p.price, p.currency, p.store_name, p.image_url, p.product_link,
            AVG(r.rating) AS avg_rating, COUNT(r.rating) AS num_ratings
        FROM products p
        LEFT JOIN reviews r ON p.product_id = r.product_id
        GROUP BY p.product_id
        """

        # Load data from MySQL database using SQLAlchemy engine
        df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("No products found in the database.")
            return None, None

        return df, query

    except Exception as e:
        st.error(f"Error loading data: {e}")

    finally:
        # Close the database connection
        if 'conn' in locals():
            conn.close()
            engine.dispose()

    # Return None if an error occurs
    return None, None

selected_df, query = load_data()

# Preprocessing function
def preprocess_text(text):
    # Use a more robust tokenizer
    tokens = word_tokenize(text.lower())
    # Remove punctuation attached to words
    tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
    # Remove stopwords
    stop_words = set(nltk.corpus.stopwords.words("english"))
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # Join tokens back into a string
    processed_text = " ".join(filtered_tokens)
    return processed_text

# Create TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()

# Fit the vectorizer on the consolidated textual data
text_embeddings = tfidf_vectorizer.fit_transform(selected_df['product_name'].apply(preprocess_text))

def stars_from_rating(avg_rating, num_ratings):
    if avg_rating is None or num_ratings == 0:
        return "☆☆☆☆☆ (0)"
    else:
        full_stars = int(avg_rating)
        empty_star = "☆"
        colored_star = "<span style='color:gold;'>★</span>"
        empty_colored_star = "<span style='color:grey;'>☆</span>"
        return colored_star * full_stars + empty_colored_star * (5 - full_stars) + f" ({num_ratings})"

def search_products(selected_df, query, top_n=5, store=None, category=None, min_price=None, max_price=None):
    # Preprocess the query
    query = preprocess_text(query)
    # Use prefix matching to find products whose names start with the query
    matches = [product for product in selected_df['product_name'] if product.startswith(query)]
    # If no exact matches, use fuzzy matching to find similar products
    if not matches:
        matches = process.extract(query, selected_df['product_name'], limit=top_n)
    # Filter matches based on store
    if store:
        matches = [match for match in matches if not selected_df[(selected_df['product_name'] == match) & (selected_df['store_name'] == store)].empty]
    # Filter matches based on category
    if category:
        matches = [match for match in matches if selected_df[(selected_df['product_name'] == match) & (selected_df['category'] == category)].notna().all(1)]
    matches = process.extract(query, selected_df['product_name'], limit=top_n)
    matches = [match[0] for match in matches]  # Extract the matched string from the tuple
    # Filter matches based on price range
    if min_price is not None and max_price is not None:
        if matches:
            matches = [match for match in matches if min_price <= selected_df.loc[selected_df['product_name'] == match, 'price'].iloc[0] <= max_price]
    # Check if there are any matches after filtering
    if len(matches) == 0:
        st.warning("No products matching the filters.")
        return
    # Store the search query and matches in the search history
    search_history.append((query, matches))
    # Generate HTML representation of the results
    html_output = "<style>"
    html_output += ".card {"
    html_output += "   border-radius: 10px;"
    html_output += "   overflow: hidden;"
    html_output += "   box-shadow: 0 4px6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);"
    html_output += "   margin-bottom: 20px;"
    html_output += "   display: flex;"
    html_output += "   background-color: transparent;"
    html_output += "}"
    html_output += ".card-image {"
    html_output += "   flex: 1;"
    html_output += "   padding: 10px;"
    html_output += "}"
    html_output += ".card-content {"
    html_output += "   flex: 2;"
    html_output += "   padding: 10px;"
    html_output += "}"
    html_output += ".buttons {"
    html_output += "   display: flex;"
    html_output += "   justify-content: space-between;"
    html_output += "}"
    html_output += "@media (prefers-color-scheme: dark) {"
    html_output += "   .card {"
    html_output += "       background-color: #ffff;"
    html_output += "   }"
    html_output += "   .card-content h3, .card-content p {"
    html_output += "       color: #000;"
    html_output += "   }"
    html_output += "}"
    html_output += "</style>"

    # Card-based layout
    for match in matches:
        # Replace empty or None image URLs with the default image URL
        if selected_df[selected_df['product_name'] == match]['image_url'].iloc[0] and selected_df[selected_df['product_name']== match]['image_url'].iloc[0].endswith('.gif'):
            selected_df.loc[selected_df['product_name'] == match, 'image_url'] = 'https://cleanshelf.s3.eu-central-003.backblazeb2.com/product-images/default.jpg'

        html_output += "<div class='card'>"
        html_output += f"<div class='card-image'><a href='{selected_df[selected_df['product_name'] == match]['image_url'].iloc[0]}' target='_blank'><img src='{selected_df[selected_df['product_name'] == match]['image_url'].iloc[0]}' style='width:200px;height:200px; object-fit: cover;'></a></div>"
        html_output += "<div class='card-content'>"
        html_output += f"<h3>{selected_df[selected_df['product_name'] == match]['product_name'].iloc[0]}</h3>"
        html_output += f"<p><strong>Price:</strong> Ksh {int(selected_df[selected_df['product_name'] == match]['price'].iloc[0])}</p>"
        html_output += f"<p><strong>Rating:</strong> {stars_from_rating(selected_df[selected_df['product_name'] == match]['avg_rating'].iloc[0], selected_df[selected_df['product_name'] == match]['num_ratings'].iloc[0])}</p>"

        # Retrieve the stores that carry the product
        stores = selected_df[selected_df['product_name'] == match]['store_name'].tolist()
        html_output += f"<p><strong>Store:</strong> {', '.join(stores)}</p>"

        html_output += "<div class='buttons'>"

        # View product button
        html_output += f"<a href='{selected_df[selected_df['product_name'] == match]['product_link'].iloc[0]}' target='_blank'><button>View Product</button></a>"

        html_output += "</div>"  # Close buttons div

        html_output += "</div>"  # Close card-content div
        html_output += "</div>"  # Close card div
        

    # Display the HTML output
    st.markdown(html_output, unsafe_allow_html=True)

    # Custom CSS styling
    st.markdown(
        """
        <style>
        /* Title font */
        .title {
            font-family: 'Montserrat Bold', sans-serif;
            font-size: 25px;
        }

        /* Text font */
        body {
            font-family: 'Montserrat Classic', sans-serif;
            font-size: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Create the search form using Streamlit
def main():
    st.markdown(background_image_search, unsafe_allow_html=True)
    st.markdown("""
            <h1 style='text-align: center;color: black'>SEARCH FOR PRODUCTS</h1>
            """, unsafe_allow_html=True)

    search_query = st.text_input("Search:")
    top_n = st.number_input("Number of Products:", min_value=1, max_value=30, value=5)
    store = st.selectbox("By Store (optional):", [None, 'Naivas', 'Carrefour', 'Cleanshelf', 'E-Mart', 'GreenspoonGO'])
    # categories = st.selectbox("By Category (optional):", ['Fruits & Vegetables', 'Dairy', 'Meat & Fish', 'Bakery', 'Beverages', 'Household', 'Personal Care', 'Baby Care', 'Pet Care', 'Frozen Foods', 'Snacks', 'Condiments', 'Breakfast Cereals', 'Canned Foods', 'Baking Supplies', 'Meal Kits', 'Meal Replacements', 'Soups', 'Juices', 'Teas', 'Coffees'])
   
    # pricing = st.selectbox("By Price Level (optional):", [None, "Budget", "Premium", "Mid-range"])
    min_price, max_price = st.slider("Price Range", min_value=0, max_value=5000, step=50, value=(0, 5000))

    if st.button("Search"):
        search_products(selected_df, query=search_query, top_n=top_n, store=store, min_price=min_price, max_price=max_price)

if __name__ == "__main__":
    main()