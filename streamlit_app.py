import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Customize Your Smoothie", page_icon="🥤")

st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# Name input
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# --------------------------------------------------
# Snowflake connection
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# Snowpark -> Pandas (so we can use loc)
# --------------------------------------------------
my_dataframe = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

pd_df = my_dataframe.to_pandas()

# --------------------------------------------------
# Multiselect should use FRUIT_NAME column (like lesson)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"],
    max_selections=5
)

# --------------------------------------------------
# For each selected fruit: get SEARCH_ON using loc/iloc
# and show nutrition info below (visual like screenshot)
# --------------------------------------------------
if ingredients_list:

    for fruit_chosen in ingredients_list:

        # ✅ Lesson line (loc + iloc)
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # ✅ Sentence should look good (like screenshot)
        st.write("The search value for", fruit_chosen, "is", search_on, ".")

        # Section title
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # ✅ IMPORTANT: call API with search_on (not fruit_chosen)
        url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        response = requests.get(url, timeout=10)

        # Try to display in a table-like way (like screenshot)
        try:
            data = response.json()

            # If API returns an error, show it but keep UI clean
            if isinstance(data, dict) and "error" in data:
                st.dataframe(pd.DataFrame([{"value": data["error"]}]))
            else:
                # If dict -> show as key/value table
                if isinstance(data, dict):
                    st.dataframe(pd.DataFrame(list(data.items()), columns=["key", "value"]))
                # If list -> show as table
                elif isinstance(data, list):
                    st.dataframe(pd.DataFrame(data))
                else:
                    st.write(data)

        except Exception:
            st.write("Could not parse API response.")
            st.write(response.text)
