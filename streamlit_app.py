import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Snowpark -> Pandas (for loc/iloc)
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)
pd_df = my_dataframe.to_pandas()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

def render_fruityvice_style_table(api_json: dict):
    """
    Convert Fruityvice-like JSON into the table seen in the lesson screenshot:
    index: nutrient (carbs/fat/protein/sugar)
    columns: family, genus, id, name, nutrition, order
    """
    if not isinstance(api_json, dict):
        st.write(api_json)
        return

    if "error" in api_json:
        # keep it readable
        st.error(api_json["error"])
        return

    nutritions = api_json.get("nutritions") or api_json.get("nutrition")
    if not isinstance(nutritions, dict):
        # fallback
        st.write(api_json)
        return

    base_cols = {
        "family": api_json.get("family"),
        "genus": api_json.get("genus"),
        "id": api_json.get("id"),
        "name": api_json.get("name"),
        "order": api_json.get("order"),
    }

    rows = []
    for nutrient_name, nutrient_value in nutritions.items():
        row = dict(base_cols)
        row["nutrition"] = nutrient_value
        row["nutrient"] = nutrient_name
        rows.append(row)

    df = pd.DataFrame(rows).set_index("nutrient")
    st.dataframe(df, use_container_width=True)

if ingredients_list:
    for fruit_chosen in ingredients_list:

        # loc/iloc (lesson requirement)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # IMPORTANT: the API key must match what the API expects (usually singular)
        # So make sure SEARCH_ON is correct in the table.
        url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        r = requests.get(url, timeout=10)

        try:
            data = r.json()
        except Exception:
            st.error("API did not return JSON.")
            st.write(r.text)
            continue

        render_fruityvice_style_table(data)

st.divider()
st.subheader("Admin")

mark_filled = st.button("Mark Order as Filled")

if mark_filled:
    if not name_on_order or not name_on_order.strip():
        st.error("Please enter the Name on Smoothie first.")
    else:
        safe_name = name_on_order.strip().replace("'", "''")

        update_stmt = f"""
            UPDATE SMOOTHIES.PUBLIC.ORDERS
            SET ORDER_FILLED = TRUE
            WHERE NAME_ON_ORDER = '{safe_name}'
              AND ORDER_FILLED = FALSE
        """
        session.sql(update_stmt).collect()
        st.success(f"Order for {name_on_order.strip()} marked as FILLED.")

