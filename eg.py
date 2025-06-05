import mysql.connector
import pandas as pd
import numpy as np

# Database connection setup
def init_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Assuming you're using the root user
        password="",  # No password
        database="recommender"
    )

# Generate dummy ratings (1 to 5) with a higher probability for 4 and 5
ratings = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.15, 0.35, 0.35], size=1000)

# Generate dummy review texts based on ratings
def generate_review_text(rating):
    if rating == 5:
        return np.random.choice(["Great product!", "Awesome!", "Highly recommended.", "Best purchase ever!", "Excellent quality.", "I love it!"])
    elif rating == 4:
        return np.random.choice(["Great product!", "Awesome!", "Highly recommended.", "Best purchase ever!", "Excellent quality.", "Decent product.", "Okay, but could be better.", "I like it."])
    elif rating == 3:
        return np.random.choice(["Decent product.", "Okay, but could be better.", "Average quality.", "Not bad, but not great.", "Fair product.", "It's alright."])
    elif rating == 2:
        return np.random.choice(["Waste of money.", "Poor quality.", "Disappointing.", "Would not recommend.", "Regret buying it."])
    else:
        return np.random.choice(["Terrible experience.", "Waste of money.", "Poor quality.", "Disappointing.", "Would not recommend.", "I regret buying it."])

# Connect to the database
conn = init_connection()
cursor = conn.cursor()

# Fetch user IDs
cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

# Fetch product IDs
cursor.execute("SELECT product_id FROM products")
product_ids = [row[0] for row in cursor.fetchall()]

# Generate variable number of ratings per product
ratings_data = []
for product_id in product_ids:
    num_ratings = np.random.randint(36, 76)  # Generate random number of ratings (1 to 35)
    for _ in range(num_ratings):
        user_id = np.random.choice(user_ids)
        rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.1, 0.15, 0.35, 0.35])  # Bias towards 4 and 5
        review_text = generate_review_text(rating)
        ratings_data.append((user_id, product_id, rating, review_text))

# Create a DataFrame for the dummy reviews
dummy_reviews = pd.DataFrame(ratings_data, columns=['user_id', 'product_id', 'rating', 'review_text'])

# Print the first few rows of the dummy reviews
dummy_reviews.to_csv('yaha_reviews.csv', index=False)

# Close the database connection
conn.close()
