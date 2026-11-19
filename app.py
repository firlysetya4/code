import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# ===============================
# Setup koneksi database SQLite
# ===============================

DB_NAME = "keuangan.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_table():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT,
                tipe TEXT,
                item TEXT,
                harga REAL,
                satuan INTEGER,
                diskon REAL,
                keterangan TEXT,
                total REAL
            )
        """)
create_table()

# ===============================
# Fungsi tambah transaksi
# ===============================
def tambah_transaksi(tanggal, tipe, item, harga, satuan, diskon, keterangan):
    subtotal = harga * satuan
    total = subtotal - diskon
    if total < 0:
        st.error("Diskon tidak boleh lebih besar dari subtotal!")
        return
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transaksi (tanggal, tipe, item, harga, satuan, diskon, keterangan, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tanggal, tipe, item, harga, satuan, diskon, keterangan, total))

# ===============================
# Fungsi ambil semua data
# ===============================
def ambil_data():
    with get_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM transaksi ORDER BY tanggal DESC, id DESC", conn)
    return df

# ===============================
# Streamlit UI
# ===============================
st.title("Aplikasi Keuangan Sederhana")

menu = st.sidebar.selectbox("Menu", ["Dashboard", "Input Transaksi", "Riwayat Transaksi"])

if menu == "Input Transaksi":
    st.header("Input Transaksi Baru")
    with st.form("form_input"):
        tanggal = st.date_input("Tanggal", date.today())
        tipe = st.selectbox("Tipe", ["Pemasukan", "Pengeluaran"])
        item = st.text_input("Item")
        harga = st.number_input("Harga per satuan (Rp)", min_value=0.0, step=1000.0)
        satuan = st.number_input("Jumlah satuan", min_value=1, step=1)
        diskon = st.number_input("Diskon (Rp)", min_value=0.0, step=1000.0)
        keterangan = st.text_area("Keterangan")
        submitted = st.form_submit_button("Simpan")

        if submitted:
            if item.strip() == "":
                st.error("Nama item wajib diisi!")
            else:
                tambah_transaksi(str(tanggal), tipe, item, harga, satuan, diskon, keterangan)
                st.success("Transaksi berhasil disimpan!")

elif menu == "Dashboard":
    st.header("Dashboard Ringkasan")
    df = ambil_data()

    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        pemasukan = df.loc[df["tipe"] == "Pemasukan", "total"].sum()
        pengeluaran = df.loc[df["tipe"] == "Pengeluaran", "total"].sum()
        saldo = pemasukan - pengeluaran

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pemasukan (Rp)", f"{pemasukan:,.0f}".replace(",", "."))
        col2.metric("Total Pengeluaran (Rp)", f"{pengeluaran:,.0f}".replace(",", "."))
        col3.metric("Saldo (Rp)", f"{saldo:,.0f}".replace(",", "."))

elif menu == "Riwayat Transaksi":
    st.header("Riwayat Transaksi")
    df = ambil_data()

    if df.empty:
        st.info("Belum ada data transaksi.")
    else:
        tipe_filter = st.selectbox("Filter Tipe Transaksi", ["Semua", "Pemasukan", "Pengeluaran"])
        if tipe_filter != "Semua":
            df = df[df["tipe"] == tipe_filter]

        st.dataframe(df[["id","tanggal","tipe","item","harga","satuan","diskon","total","keterangan"]].sort_values(by=["tanggal","id"], ascending=[False, False]))

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", data=csv, file_name="riwayat_transaksi.csv", mime="text/csv")
