import pandas as pd
import streamlit as st
import plotly.express as px

SECRET_TOKEN = "Dfd0PosPqs"

# Check if the provided token matches the secret token
user_token = st.text_input("Enter your token:", type="password")
if user_token != SECRET_TOKEN:
    st.error("Unauthorized")
    st.stop()

st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

@st.cache_data
def read_data():
    df = pd.read_excel(
        io='data/sales.xlsx',
        engine='openpyxl',
        sheet_name='Sales',
        skiprows=3,
        usecols='B:R',
    )
    df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour

    return df

df = read_data()

# Creating sidebar with filters
st.sidebar.header("Filters:")

city_values = df["City"].unique()
customer_type_values = df["Customer_type"].unique()
gender_values = df["Gender"].unique()

# Displaying 3 main filters in sidebar
city_filter = st.sidebar.multiselect("Select the City:", options=city_values, default=city_values)
customer_type_filter = st.sidebar.multiselect("Select the Customer Type:", options=customer_type_values, default=customer_type_values)
gender_filter = st.sidebar.multiselect("Select the Gender:", options=gender_values, default=gender_values)

# Choosing data based on filters
df_selection = df.query("City == @city_filter & Customer_type == @customer_type_filter & Gender == @gender_filter")
if df_selection.empty:
    st.warning("No data available!")
    st.stop()

total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_tx = round(df_selection["Total"].mean(), 2)

# Showing main stats in 3 columns
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Sales:")
    st.subheader(f"$ {total_sales:,}")
with middle_column:
    st.subheader("Average Rating:")
    st.subheader(f"{star_rating}")
with right_column:
    st.subheader("Average Sales:")
    st.subheader(f"$ {average_sale_by_tx}")

st.markdown("""---""")

# Sales by Product Line
sales_by_product_line = df_selection.groupby("Product line")[["Total"]].sum().sort_values("Total").reset_index()
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y="Product line",
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# Sales by Hour
sales_by_hour = df_selection.groupby("Hour")[["Total"]].sum().reset_index()
fig_hourly_sales = px.bar(
    sales_by_hour,
    x="Hour",
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)

hide_st_style = """
                <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                </style>
                """
st.markdown(hide_st_style, unsafe_allow_html=True)
