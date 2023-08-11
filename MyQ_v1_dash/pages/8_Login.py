import webbrowser
import streamlit as st

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>', unsafe_allow_html=True)

st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def display_subscription_message():

    url = 'https://buy.stripe.com/6oEaHAaZG6s0a4g4gg'

    st.markdown(
        f'''
            <a href={url}>
            <button style="background-color: LightGrey; color: black; border: none; 
                            padding: 10px 20px; border-radius: 4px; font-weight: bold;
                            text-decoration: none; cursor: pointer; 
                            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);">
                Subscribe Now!
            </button>
        </a>
        ''',
        unsafe_allow_html=True
    )


# Define the valid usernames and passwords
valid_credentials = {
    "emma": "emmasilk",
    "ryan": "ryan123",
    "admin": "admin",
}

# Define the login form
def login():
    st.title("Login")
    st.write("Please enter your credentials to log in.")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("Log in"):
            if username in valid_credentials and password == valid_credentials[username]:
                st.success(f"Logged in as {username}")
                # Store the username in session state
                st.session_state.username = username

            else:
                st.error("Invalid username or password")

        display_subscription_message()


# Define the home page
def home():
    st.title("Home")
    st.write(f"Welcome, {st.session_state.username}!")


# Check if the user is logged in
if "username" not in st.session_state:
    # If the user is not logged in, show the login form
    login()
else:
    # If the user is logged in, show the home page and logout button
    home()
    if st.button("Logout"):
        # Remove the username from session state and redirect to the login page
        del st.session_state["username"]
        st.experimental_rerun()






