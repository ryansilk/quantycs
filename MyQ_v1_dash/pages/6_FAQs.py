import streamlit as st

st.set_page_config(layout="wide")

st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.write('<style>div.row-widget.stRadio > div{display: flex; flex-direction: row; align-items: left;}</style>', unsafe_allow_html=True)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- FAQ ---
st.write("")
st.write("---")
st.subheader(":raising_hand: FAQ")
faq = {
    "How do I log in?": "Once you have subscribed, we will email login details to the email you subscribed with to get access to all the cool content!",
    "How often is the data updated?": "The data is updated frequently, usually on a daily or hourly basis, depending on the specific data type.",
    "Can the app be used for real-time trading?": "The app is designed to provide users with the latest data and analysis, but it is not intended for real-time trading. Users should always consult with their financial advisor before making any investment decisions.",
    "Is there a fee to use the app?": "Free users have access to 5 pre-determined stocks on the screener page, alongside 1 pre-determined stock on the dashboard page.",
}
for question, answer in faq.items():
    with st.expander(question):
        st.write(answer)

st.write("If you have any questions, click the below link, fill in the form and we'll get back to you within 24 hours!")

if st.button("Ask Away!"):
        # Update session state to navigate to the contact page
        st.session_state.page = "contact"
