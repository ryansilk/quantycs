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

CONTACT_EMAIL = "ryansilk232@gmail.com"

# --- CONTACT FORM ---
st.write("")
st.write("---")
st.subheader(":mailbox: Have A Question? Ask Away!")

contact_form = f"""
<form action="https://formsubmit.co/{CONTACT_EMAIL}" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required style="width: 300px;"><br><br>
     <input type="email" name="email" placeholder="Your email" required style="width: 300px;"><br><br>
     <textarea name="message" placeholder="Your message here" style="width: 300px;"></textarea><br><br>
     <button type="submit" class="button">Send ✉</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

