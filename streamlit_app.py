import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------------
# Snowflake connection
# -------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------------
# Load fruit options (Snowpark -> Pandas)
# -------------------------
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

pd_df = my_dataframe.to_pandas()
pd_df["FRUIT_NAME"] = pd_df["FRUIT_NAME"].astype(str).str.strip()
pd_df["SEARCH_ON"] = pd_df["SEARCH_ON"].astype(str).str.strip()

fruit_list = sorted(pd_df["FRUIT_NAME"].dropna().unique())

# -------------------------
# Inputs
# -------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Build ingredients string for the order table
ingredients_string = ""
if ingredients_list:
    ingredients_string = " ".join(ingredients_list) + " "

# -------------------------
# Nutrition preview (optional)
# -------------------------
def render_fruityvice_style_table(api_json: dict):
    if not isinstance(api_json, dict):
        st.write(api_json)
        return

    if "error" in api_json:
        st.error(api_json["error"])
        return

    nutritions = api_json.get("nutritions") or api_json.get("nutrition")
    if not isinstance(nutritions, dict):
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
    st.divider()
    st.subheader("Nutrition Preview")

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        r = requests.get(url, timeout=10)

        try:
            data = r.json()
        except Exception:
            st.error("API did not return JSON.")
            st.write(r.text)
            continue

        st.caption(f"{fruit_chosen} Nutrition Information")
        render_fruityvice_style_table(data)

# -------------------------
# Actions (buttons always visible)
# -------------------------
st.divider()
col1, col2 = st.columns(2)

with col1:
    submit_order = st.button("Submit Order")

with col2:
    mark_filled = st.button("Mark Order as Filled")

# -------------------------
# Button behavior
# -------------------------
if submit_order and name_on_order and ingredients_string:
    insert_sql = f"""
        insert into smoothies.public.orders (name_on_order, ingredients)
        values ('{name_on_order}', '{ingredients_string}')
    """
    session.sql(insert_sql).collect()
    st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

if mark_filled and name_on_order:
    update_sql = f"""
        update smoothies.public.orders
        set order_filled = true
        where name_on_order = '{name_on_order}'
          and order_filled = false
    """
    session.sql(update_sql).collect()
    st.success(f"All open orders for {name_on_order} marked as filled.", icon="✅")
