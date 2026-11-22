"""Streamlit form that calls the Flask sales API."""

import os

import requests
import streamlit as st

# Inside Docker Compose the backend service name resolves to the API container
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860").rstrip("/")

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write(
    "Enter a product and store profile. The app asks the Flask service for the predicted product-store sales."
)

st.subheader("Product and store details")
product_weight = st.number_input("Product weight", min_value=0.0, value=12.66, step=0.01)
product_sugar_content = st.selectbox(
    "Product sugar content",
    ["Low Sugar", "Regular", "No Sugar"],
)
product_allocated_area = st.number_input(
    "Product allocated area",
    min_value=0.0,
    max_value=1.0,
    value=0.027,
    step=0.001,
    format="%.3f",
)
product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08, step=0.01)
store_size = st.selectbox("Store size", ["Small", "Medium", "High"])
store_location_city_type = st.selectbox(
    "Store location city type",
    ["Tier 1", "Tier 2", "Tier 3"],
)
store_type = st.selectbox(
    "Store type",
    ["Food Mart", "Supermarket Type1", "Supermarket Type2", "Departmental Store"],
)
product_id_char = st.selectbox("Product id prefix", ["FD", "DR", "NC"])
store_age_years = st.number_input("Store age (years)", min_value=0, value=16, step=1)
product_type_category = st.selectbox(
    "Product type category",
    ["Perishables", "Non Perishables"],
)

payload = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar_content,
    "Product_Allocated_Area": product_allocated_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_location_city_type,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": int(store_age_years),
    "Product_Type_Category": product_type_category,
}

if st.button("Predict sales"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
        if response.ok:
            sales = response.json()["predicted_sales"]
            st.success(f"Predicted product-store sales: {sales:,.2f}")
        else:
            st.error(response.text)
    except requests.RequestException as exc:
        st.error(f"Could not reach the backend at {BACKEND_URL}. {exc}")
