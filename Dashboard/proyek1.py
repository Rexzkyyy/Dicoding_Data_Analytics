import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency
from function import DataAnalisis
import datetime as dt

# Set page configuration
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# Set style for seaborn
sns.set(style='dark')

# Import data
all_df = pd.read_csv("all_df.csv")

# Convert relevant columns to datetime
datetime_cols = [
    "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", 
    "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"
]

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Sort values by order_approved_at
all_df.sort_values(by="order_approved_at", inplace=True)

# Reset index
all_df.reset_index(drop=True, inplace=True)

# Get the minimum and maximum dates
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# ================= Sidebar ========================
with st.sidebar:
    # Title
    st.title("Data E-Commerce")

    # Display an image logo
    st.image("gambar1.jpg", use_column_width=True)

    # Date Range selection
    start_date, end_date = st.date_input(
        label="Pilih Rentang Waktu",
        value=[min_date.date(), max_date.date()],
        min_value=min_date.date(),
        max_value=max_date.date()
    )

# Filter the dataframe based on the selected date range
main_df = all_df[(all_df["order_approved_at"] >= pd.Timestamp(start_date)) & 
                 (all_df["order_approved_at"] <= pd.Timestamp(end_date))]

# Initialize custom functions 
function = DataAnalisis(main_df)

# Data for visualization
daily_orders_df = function.create_daily_orders_df()
sum_spend_df = function.create_sum_spend_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
city_df = function.create_customer_city_df()
state_df = function.create_customer_state_df()
rfm_df = function.create_rfm_df()




# ================= Main Content ========================
# Adding title with glowing effect
st.markdown(
    """
    <style>
    .glow-title {
        font-size: 50px;
        color: #333;
        text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ffcc00, 0 0 20px #ffcc00;
        animation: glow 1.5s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            text-shadow: 0 0 5px #ffcc00, 0 0 10px #ffcc00, 0 0 15px #ffcc00, 0 0 20px #ffcc00;
        }
        to {
            text-shadow: 0 0 10px #ffcc00, 0 0 20px #ffcc00, 0 0 30px #ffcc00, 0 0 40px #ffcc00;
        }
    }
    </style>
    <h1 class="glow-title">📊 E-commerce Dashboard</h1>
    """, unsafe_allow_html=True
)

# Display total orders and revenue
st.subheader('Orderan Harian')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df["order_count"].sum()
    st.metric(label="Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "BRL", locale="pt_BR") 
    st.metric(label="Total Revenue", value=total_revenue)

# Daily orders plot
plt.figure(figsize=(12, 6))
plt.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o',
    linestyle='-',
    linewidth=2,
    color="#1f77b4"
)
plt.title("Jumlah Pesanan per Hari", fontsize=22, fontweight='bold')
plt.xlabel("Tanggal", fontsize=14)
plt.ylabel("Jumlah Pesanan", fontsize=14)
plt.xticks(fontsize=12, rotation=45, ha='right')
plt.yticks(fontsize=12)
plt.grid(True, which='both', linestyle='--', linewidth=0.7)
plt.tight_layout()
st.pyplot(plt)

# Customer Spend Money section
st.subheader("Pengeluaran Pelanggan")

col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale="pt_BR")
    st.metric(label="Total Pengeluaran", value=total_spend)

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="pt_BR")
    st.metric(label="Pengeluaran Rata-rata", value=avg_spend)

# Plot customer spending
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],  # Ensure this column name matches your DataFrame
    sum_spend_df["total_spend"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.set_title('Pengeluaran Pelanggan Harian', fontsize=18)
ax.set_xlabel('Tanggal', fontsize=14)
ax.set_ylabel('Jumlah Pengeluaran', fontsize=14)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=12)

st.pyplot(fig)

# Order Items section
st.subheader("Item Pesanan")

col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.metric(label="Total Item", value=total_items)

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.metric(label="Rata-rata Item", value=avg_items)

# Bar plots for most and least sold products
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 12))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Most sold products
sns.barplot(
    x="product_count",
    y="product_category_name_english",
    data=sum_order_items_df.head(5),
    palette=colors,
    ax=ax[0]
)
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[0].set_title("Produk Paling Banyak Terjual", loc="center", fontsize=30)
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis='x', labelsize=20)

# Least sold products
sns.barplot(
    x="product_count",
    y="product_category_name_english",
    data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5),
    palette=colors,
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk Paling Sedikit Terjual", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=20)

st.pyplot(fig)

# Review Score section
st.subheader("Skor Ulasan")

col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.metric(label="Rata-rata Skor Ulasan", value=f"{avg_review_score:.2f}")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.metric(label="Skor Ulasan Paling Umum", value=most_common_review_score)

# Bar plot for review scores
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x=review_score.index,
    y=review_score.values,
    order=review_score.index,
    palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
)
plt.title("Rating dari Pelanggan untuk Layanan", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Total Pelanggan")
plt.xticks(rotation=45)
st.pyplot(fig)

# Customer Distribution section
st.title("Distribusi Pelanggan")

# Tabs
tab1, tab2 = st.tabs(["Distribusi per Ibu Kota", "Distribusi per Negara Bagian"])

with tab1:
    # Customer Distribution by City
    st.subheader("Distribusi Pelanggan per Ibu Kota")

    # Plot customer distribution by city
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        x="customer_count",
        y="city",
        data=city_df.head(10),  # Show top 10 cities
        palette="viridis"
    )
    ax.set_title('Top 10 Ibu Kota dengan Jumlah Pelanggan Terbanyak', fontsize=18)
    ax.set_xlabel('Jumlah Pelanggan', fontsize=14)
    ax.set_ylabel('Ibu Kota', fontsize=14)
    st.pyplot(fig)

with tab2:
    # Customer Distribution by State
    st.subheader("Distribusi Pelanggan per Negara Bagian")

    # Plot customer distribution by state
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        x="customer_count",
        y="state",
        data=state_df.head(10),  # Show top 10 states
        palette="viridis"
    )
    ax.set_title('Top 10 Negara Bagian dengan Jumlah Pelanggan Terbanyak', fontsize=18)
    ax.set_xlabel('Jumlah Pelanggan', fontsize=14)
    ax.set_ylabel('Negara Bagian', fontsize=14)
    st.pyplot(fig)
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]


#buat disini bar plot visaul RFM 

# ================= RFM Analysis ========================
st.title("Analisis RFM - 5 Pelanggan Teratas")
st.subheader("Visualisasi RFM Berdasarkan Top 5 Pelanggan")

# Define plot colors
plot_colors = ["#72BCD4", "#FF9A9E", "#70c2a5"]

# Create a figure and axis objects
fig, ax = plt.subplots(1, 3, figsize=(18, 6))

# Plot Recency
recency_df = rfm_df.sort_values(by="Recency", ascending=True).head(5)
sns.barplot(
    x=recency_df.index.astype(str),  # Using index as x-axis labels
    y="Recency",
    data=recency_df,
    palette=[plot_colors[0]],  # Single color for consistency
    ax=ax[0]
)
ax[0].set_ylabel("Recency (hari)", fontsize=14)
ax[0].set_xlabel("Top 5 Pelanggan", fontsize=14)
ax[0].set_title("Top 5 Pelanggan Berdasarkan Recency", fontsize=16)
ax[0].tick_params(axis='x', labelsize=12)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45)  # Rotate for readability
ax[0].set_xticks([])  # Remove x-axis ticks

# Plot Frequency
frequency_df = rfm_df.sort_values(by="Frequency", ascending=False).head(5)
sns.barplot(
    x=frequency_df.index.astype(str),  # Using index as x-axis labels
    y="Frequency",
    data=frequency_df,
    palette=[plot_colors[1]],  # Single color for consistency
    ax=ax[1]
)
ax[1].set_ylabel("Frequency", fontsize=14)
ax[1].set_xlabel("Top 5 Pelanggan", fontsize=14)
ax[1].set_title("Top 5 Pelanggan Berdasarkan Frequency", fontsize=16)
ax[1].tick_params(axis='x', labelsize=12)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45)  # Rotate for readability
ax[1].set_xticks([])  # Remove x-axis ticks

# Plot Monetary
monetary_df = rfm_df.sort_values(by="Monetary", ascending=False).head(5)
sns.barplot(
    x=monetary_df.index.astype(str),  # Using index as x-axis labels
    y="Monetary",
    data=monetary_df,
    palette=[plot_colors[2]],  # Single color for consistency
    ax=ax[2]
)
ax[2].set_ylabel("Monetary (BRL)", fontsize=14)
ax[2].set_xlabel("Top 5 Pelanggan", fontsize=14)
ax[2].set_title("Top 5 Pelanggan Berdasarkan Monetary", fontsize=16)
ax[2].tick_params(axis='x', labelsize=12)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45)  # Rotate for readability
ax[2].set_xticks([])  # Remove x-axis ticks

# Main title for the entire figure
plt.suptitle("Pelanggan Terbaik Berdasarkan Parameter RFM", fontsize=20)

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust to fit the main title

# Display the plot in Streamlit
st.pyplot(fig)

st.markdown("""
    <div style="text-align: center; font-size: 24px; color: #888888;">
        ✨ Copyright (c) Ikhsanuddin Rezki - 2024 🚀
    </div>
    """, unsafe_allow_html=True)

print("Recency values:", rfm_df['Recency'].describe())


