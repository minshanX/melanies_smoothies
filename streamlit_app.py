import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Set up app title
st.title(f" :cup_with_straw: Example Streamlit App :cup_with_straw: {st.__version__}")
st.write("Choose the fruits or submit preset orders.")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Manual order form
name_on_order = st.text_input("Name on Smoothie:")
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Show nutrition info
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        st.subheader(f'{fruit_chosen} Nutrition Information')
        try:
            response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
            st.dataframe(data=response.json(), use_container_width=True)
        except:
            st.error("Failed to fetch nutrition info.")

    # Submit manual order
    if st.button('Submit Order'):
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string.strip()}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success('Your Smoothie is ordered!')

# --- Auto-fill buttons for Divya and Xi ---

st.divider()
st.subheader("Quick Fill Orders")

# Divya's Order
if st.button("Submit Divya's Order"):
    ingredients = "Dragon Fruit Guava Figs Jackfruit Blueberries"
    session.sql(f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('{ingredients}', 'Divya', TRUE)
    """).collect()
    st.success("Divya's order submitted!")

# Xi's Order
if st.button("Submit Xi's Order"):
    ingredients = "Vanilla Fruit Nectarine"
    session.sql(f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order, order_filled)
        VALUES ('{ingredients}', 'Xi', TRUE)
    """).collect()
    st.success("Xi's order submitted!")
