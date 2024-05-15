import streamlit as st
import pandas as pd
import re
import nltk
import search
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine
from styles import background_image_search

        # Download NLTK data (if not already downloaded)
# nltk.download('punkt')
# nltk.download('stopwords')

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
            # Remove special characters and convert to lowercase
            text = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
            # Tokenize the text
            tokens = word_tokenize(text)
            # Load stopwords only once outside the function
            stop_words = set(stopwords.words("english"))
            # Remove stopwords
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



def search_products(query, top_n=5, store=None, pricing=None, min_price=None, max_price=None):
    # Preprocess the query
    query = preprocess_text(query)
    # Transform the query into an embedding using the TF-IDF vectorizer
    query_embedding = tfidf_vectorizer.transform([query])
    # Calculate the cosine similarity between the query embedding and all product embeddings
    similarity_scores = cosine_similarity(query_embedding, text_embeddings)
    # Get the indices of the top-N most similar products
    top_indices = similarity_scores.argsort()[0][-top_n:][::-1]
    # Retrieve the top-N recommended products
    recommendations = selected_df.iloc[top_indices]

    # Filter recommendations based on store
    if store:
        recommendations = recommendations[recommendations['store_name'] == store]

    # Filter recommendations based on pricing label
    if pricing:
        recommendations = recommendations[recommendations['price_tags'] == pricing]

    # Filter recommendations based on price range
    if min_price is not None and max_price is not None:
        recommendations = recommendations[(recommendations['price'] >= min_price) & (recommendations['price'] <= max_price)]

    # Check if there are any recommendations after filtering
    if len(recommendations) == 0:
        st.warning("No products matching the filters.")
        return

    # Store the search query and recommendations in the search history
    search_history.append((query, recommendations))

    # Generate HTML representation of the results
    html_output = "<style>"
    html_output += ".card {"
    html_output += "   border-radius: 10px;"
    html_output += "   overflow: hidden;"
    html_output += "   box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);"
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
    html_output += "       background-color: #96d6a0;"
    html_output += "   }"
    html_output += "   .card-content h3, .card-content p {"
    html_output += "       color: #000;"
    html_output += "   }"
    html_output += "}"
    html_output += "</style>"

    # Card-based layout
    for index, row in recommendations.iterrows():
        # Replace empty or None image URLs with the default image URL
        if row['image_url'] and row['image_url'].endswith('.gif'):
            row['image_url'] = 'https://cleanshelf.s3.eu-central-003.backblazeb2.com/product-images/default.jpg'

        html_output += "<div class='card'>"
        html_output += f"<div class='card-image'><a href='{row['image_url']}' target='_blank'><img src='{row['image_url']}' style='width:200px;height:200px; object-fit: cover;'></a></div>"
        html_output += "<div class='card-content'>"
        html_output += f"<h3>{row['product_name']}</h3>"
        html_output += f"<p><strong>Price:</strong> Ksh {int(row['price'])}</p>"
        html_output += f"<p><strong>Rating:</strong> {stars_from_rating(row['avg_rating'], row['num_ratings'])}</p>"

        # Retrieve the stores that carry the product
        stores = selected_df[selected_df['product_name'] == row['product_name']]['store_name'].tolist()
        html_output += f"<p><strong>Store:</strong> {', '.join(stores)}</p>"

        html_output += "<div class='buttons'>"

        # View product button
        html_output += f"<a href='{row['product_link']}' target='_blank'><button>View Product</button></a>"
        # Modify the "Review Product" button in the HTML output loop
        # html_output += f"<a href='/rate.py?product_id={row['product_id']}'><button style='cursor: pointer;'>Review Product</button></a>"





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
    st.title("Search for Grocery ")

    search_query = st.text_input("Search:")
    top_n = st.number_input("Number of Products:", min_value=1, max_value=30, value=5)
    store = st.selectbox("By Store (optional):", [None, 'Naivas', 'Carrefour', 'Cleanshelf', 'E-Mart', 'GreenspoonGO'])
    # pricing = st.selectbox("By Price Level (optional):", [None, "Budget", "Premium", "Mid-range"])
    min_price, max_price = st.slider("Price Range", min_value=0, max_value=5000, step=50, value=(0, 5000))

    if st.button("Search"):
        search.search_products(query=search_query, top_n=top_n, store=store, min_price=min_price, max_price=max_price)

if __name__ == "__main__":
    main()

