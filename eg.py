import streamlit as st
import torch
from model import MatrixFactorizationModel

# Load the checkpoint
checkpoint = torch.load('model2.pth')

# Print the keys of the checkpoint dictionary
st.write("Keys in the checkpoint:", checkpoint.keys())

# Extract the necessary information from the checkpoint
n_users = checkpoint['n_users']
n_items = checkpoint['n_items']

# Create a new model instance
model = MatrixFactorizationModel(n_users, n_items, n_factors=8)

# Load the model state dictionary
model.load_state_dict(checkpoint['model_state_dict'])

# Set the model to evaluation mode
model.eval()

# Continue with the rest of your Streamlit app...
