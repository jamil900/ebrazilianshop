import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Membaca dataset
all_df = pd.read_csv("all_data.csv")

# Konversi kolom order_purchase_timestamp ke tipe datetime
all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Mendapatkan nilai minimum dan maksimum dari order_purchase_timestamp
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

# Bagian Sidebar
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://t3.ftcdn.net/jpg/02/98/18/60/360_F_298186090_Rimyxol4jsYvYbQg1i6sttQ5N3oebXgt.jpg")
    
    # Row 1 dengan 2 kolom
    row1_col1, row1_col2 = st.columns(2)
    
    # Menambahkan konten ke masing-masing kolom di dalam sidebar
    start_date = row1_col1.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
    selected_hour_start = row1_col2.selectbox('Start Hour', list(range(24)), index=0)

    # Row 2 dengan 2 kolom
    row2_col1, row2_col2 = st.columns(2)
    
    # Menambahkan konten ke masing-masing kolom di dalam sidebar
    end_date = row2_col1.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)
    selected_hour_end = row2_col2.selectbox('End Hour', list(range(24)), index=23)

    # Row 3 dengan 2 kolom
    row3_col1, row3_col2 = st.columns(2)

    # Dropdown untuk memilih states pelanggan
    selected_station = row3_col1.selectbox('States', ['All'] + list(all_df['customer_state'].unique()), index=0)
    
    # Filter daftar kota berdasarkan state yang dipilih
    if selected_station != 'All':
        unique_cities = all_df.loc[all_df['customer_state'] == selected_station, 'customer_city'].unique()
    else:
        unique_cities = all_df['customer_city'].unique()

    # Dropdown untuk memilih kota pelanggan
    selected_city = row3_col2.selectbox('City', ['All'] + list(unique_cities), index=0)

# Filter data berdasarkan rentang waktu dan wilayah
start_datetime = pd.to_datetime(f"{start_date} {selected_hour_start}:00:00")
end_datetime = pd.to_datetime(f"{end_date} {selected_hour_end}:59:59")

filtered_df = all_df[
    (all_df['order_purchase_timestamp'] >= start_datetime) &
    (all_df['order_purchase_timestamp'] <= end_datetime)
]

if selected_station != 'All':
    filtered_df = filtered_df[filtered_df['customer_state'] == selected_station]
if selected_city != 'All':
    filtered_df = filtered_df[filtered_df['customer_city'] == selected_city]

# Hitung total pesanan
total_orders = filtered_df['order_id'].nunique()

# Hitung 5 kategori produk yang paling disukai
top_5_categories = filtered_df.groupby('product_category_name').size().reset_index(name='jumlah_pesanan')
top_5_categories = top_5_categories.sort_values(by='jumlah_pesanan', ascending=False).head(5)

# Hitung 5 kategori produk yang kurang disukai
bottom_5_categories = filtered_df.groupby('product_category_name').size().reset_index(name='jumlah_pesanan')
bottom_5_categories = bottom_5_categories.sort_values(by='jumlah_pesanan', ascending=True).head(5)

# Hitung waktu favorit pelanggan melakukan pesanan
filtered_df['Hour'] = filtered_df['order_purchase_timestamp'].dt.hour
orders_per_hour = filtered_df.groupby('Hour').size().reset_index(name='jumlah_pesanan')
orders_per_hour = orders_per_hour.sort_values(by='jumlah_pesanan', ascending=False)

# Hitung jumlah pesanan per bagian hari (order_purchase_parts_of_day)
orders_per_part_of_day = filtered_df.groupby('order_purchase_parts_of_day').size().reset_index(name='jumlah_pesanan')

# Hitung jumlah pesanan per tanggal
filtered_df['order_date'] = filtered_df['order_purchase_timestamp'].dt.date
orders_per_date = filtered_df.groupby('order_date').size().reset_index(name='jumlah_pesanan')

# Rename
orders_per_date = orders_per_date.rename(columns={
    'order_date': 'Order Date',
    'jumlah_pesanan': 'Total Orders'
})

top_5_categories = top_5_categories.rename(columns={
    'product_category_name': 'Product Category',
    'jumlah_pesanan': 'Total Orders'
})

bottom_5_categories = bottom_5_categories.rename(columns={
    'product_category_name': 'Product Category',
    'jumlah_pesanan': 'Total Orders'
})

orders_per_hour = orders_per_hour.rename(columns={
    'jumlah_pesanan': 'Total Orders'
})

orders_per_part_of_day = orders_per_part_of_day.rename(columns={
    'order_purchase_parts_of_day': 'Order By Part of Day',
    'jumlah_pesanan': 'Total Orders'
})

st.header('E-Brazilianshop :sparkles:')

# Tampilkan hasil di Streamlit
st.metric("Total Orders", total_orders)

# Tampilkan grafik jumlah pesanan per tanggal
st.write(f'Number of Orders per Date {start_datetime} To {end_datetime}, States: {selected_station if selected_station != "All" else "All"}, City: {selected_city if selected_city != "All" else "All"}')
st.bar_chart(orders_per_date.set_index('Order Date'))
st.dataframe(orders_per_date)  # Tampilkan tabel di bawah grafik

# Tampilkan 5 kategori produk yang paling disukai
st.subheader("5 Most Liked and Least Liked Product Categories")
'_Most Liked_'
st.bar_chart(top_5_categories.set_index('Product Category'), horizontal="True")
# st.dataframe(top_5_categories)

'_Least Liked_'
st.bar_chart(bottom_5_categories.set_index('Product Category'), horizontal="True")
# st.dataframe(bottom_5_categories)

# Tampilkan waktu favorit pelanggan melakukan pesanan
st.subheader("Customers' Favorite Time to Place Orders")
st.bar_chart(orders_per_hour.set_index('Hour'))
st.dataframe(orders_per_hour)

# Tampilkan grafik waktu pesanan favorit berdasarkan bagian hari
st.subheader("Favorite Order Times By Part of Day")
st.bar_chart(orders_per_part_of_day.set_index('Order By Part of Day'), horizontal="True")
st.dataframe(orders_per_part_of_day)

'''
Parts of Day

- Morning       5 am to 12 pm (noon)
- Afternoon     12 pm to 5 pm
- Evening       5 pm to 9 pm
- Night         9 pm to 4 am

source : https://www.britannica.com/dictionary/eb/qa/parts-of-the-day-early-morning-late-morning-etc
'''

st.caption('Copyright (c) Jamil Ulumudin 2025')