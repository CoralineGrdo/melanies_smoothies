import streamlit as st
from snowflake.snowpark.functions import col

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection (SniS)
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options as a plain Python list (required for st.multiselect)
fruit_rows = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
    .sort(col("FRUIT_NAME"))
    .collect()
)
fruit_options = [row["FRUIT_NAME"] for row in fruit_rows]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    options=fruit_options,
    max_selections=5
)

st.write("You selected:", ingredients_list)

time_to_insert = st.button("Submit Order")

if time_to_insert:
    if not name_on_order.strip():
        st.error("Please enter a name on Smoothie.")
    elif len(ingredients_list) == 0:
        st.error("Please select at least 1 ingredient.")
    else:
        # Build a single string: "A B C" (no trailing space)
        ingredients_string = " ".join(ingredients_list)

        # Escape single quotes to avoid breaking SQL
        safe_ingredients = ingredients_string.replace("'", "''")
        safe_name = name_on_order.strip().replace("'", "''")

        my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{safe_name}')
        """

        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order.strip()}!")
