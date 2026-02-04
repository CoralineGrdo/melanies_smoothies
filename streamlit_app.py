import streamlit as st
import requests
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --- Snowflake connection (SniS) ---
cnx = st.connection("snowflake")
session = cnx.session()

# --- Name input ---
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write("The name on your Smoothie will be:", name_on_order)

# =========================================================
# LESSON 10 DEBUG STEP: Inspect what Snowflake returns
# =========================================================
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
    .sort(col("FRUIT_NAME"))
)

st.dataframe(my_dataframe, use_container_width=True)

# Stop here on purpose (Lesson 10)
st.stop()

# =========================================================
# (Everything below will run only AFTER you comment st.stop())
# =========================================================

# Collect fruit rows for UI + API lookup
fruit_rows = my_dataframe.collect()

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
    if not name_on_order or not name_on_order.strip():
        st.error("Please enter a name on Smoothie.")
        st.stop()

    if len(ingredients_list) == 0:
        st.error("Please select at least 1 ingredient.")
        st.stop()

    # Build ingredients string
    ingredients_string = " ".join(ingredients_list)

    # Escape single quotes for SQL safety
    safe_ingredients = ingredients_string.replace("'", "''")
    safe_name = name_on_order.strip().replace("'", "''")

    insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{safe_ingredients}', '{safe_name}')
    """

    session.sql(insert_stmt).collect()
    st.success(f"✅ Your Smoothie is ordered, {name_on_order.strip()}!")

    # Show nutrition info using SEARCH_ON column
    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        search_term = fruit_search_map.get(fruit_chosen, fruit_chosen)

        try:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{search_term}",
                timeout=10
            )

            if response.status_code != 200:
                st.warning(f"Could not fetch nutrition info for {fruit_chosen}.")
                continue

            data = response.json()
            st.json(data)

        except requests.RequestException as e:
            st.warning(f"Network error fetching {fruit_chosen}: {e}")
