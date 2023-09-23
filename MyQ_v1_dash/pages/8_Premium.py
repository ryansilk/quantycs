import webbrowser
import streamlit as st

def display_subscription_message():

    url = 'https://buy.stripe.com/7sIdRK4ti85E2paeUU'

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

# --- GENERAL SETTINGS ---
STRIPE_CHECKOUT = "https://buy.stripe.com/dR67uJeBa7BweoE5kl"

DEMO_VIDEO = "https://youtu.be/PmJ9rkKGqrI"
PRODUCT_NAME = "Quantycs Premium"
PRODUCT_TAGLINE = "Ready To Take Your Trading To The Next Level? 🚀"
PRODUCT_DESCRIPTION = """
       MyQuantfolio provides everyday traders with institutional grade data, to make better informed trading decisions:

       - Gain institutional grade insight data into the stocks, bonds, commodity & FX markets!
       - Screen hundreds of stocks quantitatively
       - Analyze data using interactive charts
       - Download data into CSV or Excel
       - … and many more powerful features
       **This is your new superpower; why go to work without it?**
       """

# --- MAIN SECTION ---
st.header(PRODUCT_NAME)
st.subheader(PRODUCT_TAGLINE)
left_col, right_col = st.columns((2, 1))
with left_col:
    st.text("")
    st.write(PRODUCT_DESCRIPTION)
    display_subscription_message()
