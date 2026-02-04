import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection (SniS)
cnx = st.connection("snowflake")
session = cnx.session()

# ✅ Lesson 10: Build Snowpark DataFrame (FRUIT_NAME + SEARCH_ON)
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# ✅ Lesson 10: Convert Snowpark DataFrame -> Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# ✅ Display Pandas DataFrame so you can verify output
st.dataframe(pd_df, use_container_width=True)

# ✅ Stop here on purpose (Lesson 10)
st.stop()
