import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Nama file penyimpanan
DATA_FILE = "data_keuangan.csv"

# Fungsi untuk load data dari file csv, jika tidak ada buat dataframe kosong
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=['Tanggal'])
    else:
        df = pd.DataFrame(columns=['Tanggal','Item','Harga','Satuan','Diskon','Keterangan','Tipe','Total'])
    return df

# Fungsi untuk simpan data ke csv
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Hitung total harga per transaksi
def hitung_total(harga, satuan, diskon):
    total = (harga * satuan) - diskon
    return max(total, 0)  # jangan sampai negatif

st.title("Aplikasi Keuangan Sederhana")

# Load data transaksi
data = load_data()

# Form input data transaksi baru
with st.form("form_input"):
    st.subheader("Input Data Transaksi Baru")
    tanggal = st.date_input("Tanggal", datetime.today())
    item = st.text_input("Item")
    harga = st.number_input("Harga per satuan (Rp)", min_value=0, format="%d")
    satuan = st.number_input("Jumlah satuan", min_value=1, format="%d")
    diskon = st.number_input("Diskon (Rp)", min_value=0, format="%d")
    keterangan = st.text_area("Keterangan")
    tipe = st.selectbox("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])
    submitted = st.form_submit_button("Simpan Data")

    if submitted:
        total = hitung_total(harga, satuan, diskon)
        new_data = {
            'Tanggal': tanggal,
            'Item': item,
            'Harga': harga,
            'Satuan': satuan,
            'Diskon': diskon,
            'Keterangan': keterangan,
            'Tipe': tipe,
            'Total': total
        }
        data = data.append(new_data, ignore_index=True)
        save_data(data)
        st.success("Transaksi berhasil disimpan!")

# Dashboard dan Ringkasan
st.subheader("Dashboard Ringkasan Keuangan")

if not data.empty:
    total_pemasukan = data.loc[data['Tipe'] == 'Pemasukan', 'Total'].sum()
    total_pengeluaran = data.loc[data['Tipe'] == 'Pengeluaran', 'Total'].sum()
    saldo = total_pemasukan - total_pengeluaran

    st.metric("Saldo Saat Ini (Rp)", f"{saldo:,}")
    st.metric("Total Pemasukan (Rp)", f"{total_pemasukan:,}")
    st.metric("Total Pengeluaran (Rp)", f"{total_pengeluaran:,}")

    st.subheader("Riwayat Transaksi")
    # Tampilkan data terbaru paling atas
    st.dataframe(data.sort_values(by='Tanggal', ascending=False).reset_index(drop=True))
else:
    st.info("Belum ada data transaksi. Silakan input data di atas.")

