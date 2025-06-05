import streamlit as st
from streamlit_option_menu import option_menu
import auth
import admin
from auth import is_authenticated, is_admin, get_user_info, logout
import home, trending, search, your_reviews, rate, preference

# Database connection setup
conn = auth.init_connection()

if not auth.is_authenticated():
    auth.login_form(conn)
else:
    if is_admin():
        admin.main()  # Call the main function in the admin module
    else:
        username, _ = get_user_info(conn)  # Get the username
        menu_title = f"Welcome {username}"  # Modify the menu title to include the username
        

        class MultiApp:

            def __init__(self, menu_title):
                self.menu_title = menu_title
                self.apps = []

            def add_app(self, title, func):
                self.apps.append({
                    "title": title,
                    "function": func
                })

            def run(self):
                st.markdown(
                    """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.sidebar:
                    app = option_menu(
                        menu_title=self.menu_title,
                        options=['Home', 'Search', 'Popular', 'Review Groceries', 'Your Reviews','Preference', 'Logout'],
                        icons=['house-fill', 'search', 'bi bi-fire', 'star-fill', 'bookmark-star-fill','bi bi-bag-heart-fill','bi bi-box-arrow-right'],
                        menu_icon='cart-check-fill',
                        default_index=0,
                        styles={
                            "menu-title":{"color":"black"},
                            "container": {"padding": "5px", "background-color": "#96d6a0"},
                            "icon": {"color": "black", "font-size": "23px"},
                            "nav-link": {"color": "black", "font-size": "20px", "text-align": "left", "margin": "0px",
                                        "--hover-color": "#3a3b20"},
                            "nav-link-selected": {"background-color": "#ff4b4b", "font-weight": "normal"},
                        }
                    )

                if app == "Home":
                    home.main()
                if app == "Search":
                    search.main()
                if app == "Popular":
                    trending.main()
                if app == 'Your Reviews':
                    your_reviews.main()
                if app == 'Review Groceries':
                    rate.main()
                if app == 'Preference':
                    preference.main()
                if app == "Logout":
                    auth.logout()
                    st.rerun()

        # Database connection setup
        conn = auth.init_connection()

        if not auth.is_authenticated():
            auth.login_form(conn)
        else:
            if is_admin():
                admin.main()  # Call the main function in the admin module
            else:
                username, _ = get_user_info(conn)  # Get the username
                menu_title = f"Welcome {username}"  # Modify the menu title to include the username

                multi_app = MultiApp(menu_title)
                multi_app.run()

        conn.close()

