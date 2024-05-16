from flask import Flask, request
import mysql.connector
from auth import get_user_info

app = Flask(__name__)

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

# Handle DELETE requests to the /reviews/:id endpoint
@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review_route(review_id):
    conn = init_connection()
    delete_review(conn, review_id)
    conn.close()
    return '', 204

# Main function
def main():
    conn = init_connection()
    reviews = get_user_reviews(conn)
    
    # Add the JavaScript code to the HTML string
    html = f"""
    <script>
    // ...
    </script>
    """

    for review_id, product_id, rating, review_text, product_name, image_url, store_name, price in reviews:
        html += f"""
        <div style='
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.8), 0 1px 3px rgba(0, 0, 0, 0.08);
            margin-bottom: 20px;
            display: flex;
            background-color: #96d6a0;
        '>
            <div style='flex: 1; padding: 10px;'>
                <img src='{image_url}' style='width:200px;height:200px; object-fit: cover;'>
            </div>
            <div style='flex: 2; padding: 10px;'>
                <h2 style='margin-top:10px;margin-bottom:5px;'>{product_name}</h2>
                <p style='margin-bottom:5px;'>Rating: {rating}</p>
                <p style='margin-bottom:5px;'>Review: {review_text}</p>
                <p style='margin-bottom:5px;'>Store: {store_name}</p>
                <p style='margin-bottom:10px;'>Price: Ksh {price}</p>
                <button class="delete-button" onclick="deleteReview({review_id})">Delete</button>
            </div>
        </div>
        """

    st.markdown(html, unsafe_allow_html=True)

    conn.close()

if __name__ == "__main__":
    main()
