import streamlit as st
background_image_url = "https://i.ibb.co/BtJPmGJ/luxa-org-opacity-changed-original.jpg"
# background_image_url = "https://images.unsplash.com/photo-1506617564039-2f3b650b7010?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

background_image = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("{background_image_url}");
    background-size: 100vw 100vh;
    background-position: center;  
    background-repeat: no-repeat;
}}

[data-testid="stVerticalBlock"] {{
    background-color: rgba(0, 0, 0, 0.5); 
    color: white;
}}

[data-testid="element-container"] {{
    background-color: rgba(0, 0, 0, 0.1);
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0.1);
}}
    
[data-testid="stSidebar"] > div:first-child {{
    background: rgba(0,0,0,0.9);
}}

</style>
"""


background_image_search = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("{background_image_url}");
    background-size: 100vw 100vh;
    background-position: center;  
    background-repeat: no-repeat;
}}



[data-testid="stVerticalBlock"] {{
    background-color: rgba(255,255,255, 0.5); 
    color: black;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0.1);
}}
    
[data-testid="stSidebar"] > div:first-child {{
    background: rgba(0,0,0,0.9);
}}

</style>
"""

background_image_reviews = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("{background_image_url}");
    background-size: 100vw 100vh;
    background-position: center;  
    background-repeat: no-repeat;
}}

[data-testid="stVerticalBlock"] {{
     
    color: black;
}}

[data-testid="stHeader"] {{
    background: rgba(0,0,0,0.1);
}}
    
[data-testid="stSidebar"] > div:first-child {{
    background: rgba(0,0,0,0.9);
}}

</style>
"""

background_image_rate = f"""
<style>

[data-testid="stAppViewContainer"] > .main {{
    background-image: url("{background_image_url}");
    background-size: 100vw 100vh;
    background-position: center;  
    background-repeat: no-repeat;
}}



[data-testid="stHeader"] {{
    background: rgba(0,0,0,0.1);
}}

[data-testid="stVerticalBlock"] {{
    background-color: rgba(255,255,255); 
    color: black;
}}
    
[data-testid="stSidebar"] > div:first-child {{
    background: rgba(0,0,0,0.9);
}}

</style>
"""

background_image_preference = f"""
<style>

[data-testid="stAppViewContainer"] > .main {{
    background-image: url("{background_image_url}");
    background-size: 100vw 100vh;
    background-position: center;  
    background-repeat: no-repeat;
}}



[data-testid="stHeader"] {{
    background: rgba(0,0,0,0.1);
}}

[data-testid="stVerticalBlock"] {{
    background-color: rgba(255,255,255); 
    color: black;
}}
    
[data-testid="stSidebar"] > div:first-child {{
    background: rgba(0,0,0,0.9);
}}

</style>
"""