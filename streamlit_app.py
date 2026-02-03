import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

session = get_active_session()
fruit_df = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df,
    max_selections=5
)

st.write("You selected:", ingredients_list)

# Build a single string "A B C "
ingredients_string = ""
if ingredients_list:
    for fruit in ingredients_list:
        ingredients_string += fruit + " "

time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order:
        st.error("Please enter a name on Smoothie.")
    elif not ingredients_list:
        st.error("Please select at least 1 ingredient.")
    else:
        # Escape single quotes to avoid breaking SQL
        safe_ingredients = ingredients_string.replace("'", "''")
        safe_name = name_on_order.replace("'", "''")

        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
