import streamlit as st

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Boss"])

    if page == "Home":
        home()
    elif page == "Boss":
        boss()

def home():
    st.title("Hello")

def boss():
    st.button("Boss")

if __name__ == "__main__":
    main()