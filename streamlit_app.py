import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection (SniS)
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options WITH SEARCH_ON column
fruit_rows = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .sort(col("FRUIT_NAME"))
    .collect()
)

# List for multiselect display, dictionary for API lookup
fruit_options = [row["FRUIT_NAME"] for row in fruit_rows]
fruit_search_map = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in fruit_rows}

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

        # Show SmoothieFroot nutrition for each chosen fruit using SEARCH_ON
        for fruit_chosen in ingredients_list:
            st.subheader(f"{fruit_chosen} Nutrition Information")

            # Get the correct API search term from SEARCH_ON column
            search_term = fruit_search_map[fruit_chosen]

            smoothiefroot_response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_term}"
            )

            sf_df = st.dataframe(
                data=smoothiefroot_response.json(),
                use_container_width=True
            )
            st.stop()
