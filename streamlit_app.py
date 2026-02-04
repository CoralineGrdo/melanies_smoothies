import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------
# Name input
# -------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -------------------------
# Snowflake connection
# -------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------
# Snowpark -> Pandas (so we can use loc/iloc)
# -------------------------
my_dataframe = (
    session
        .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
        .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# -------------------------
# Multiselect from FRUIT_NAME
# -------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

# -------------------------
# Use SEARCH_ON for API calls (Lesson 10 step)
# -------------------------
if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON using Pandas loc + iloc (required by lesson)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Show the sentence (should look good)
        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        st.subheader(fruit_chosen + " Nutrition Information")

        # Use SEARCH_ON in the API request (this is the key instruction)
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        # Show response in the app
        st.dataframe(smoothiefroot_response.json(), use_container_width=True)
