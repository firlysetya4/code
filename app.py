
import streamlit as st
import pandas as pd
import sqlite3
from datetime import date

# ==========================================
# KONFIGURASI APLIKASI
# ==========================================

st.set_page_config(
    page_title="My Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

DB_NAME = "keuangan.db"

# ==========================================
# DATABASE
# ==========================================

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_database():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal TEXT,
            jenis TEXT,
            keterangan TEXT,
            kategori TEXT,
            jumlah REAL,
            satuan TEXT,
            harga REAL,
            total REAL,
            catatan TEXT
        )
    """)
    conn.commit()
    conn.close()

def tambah_transaksi(
    tanggal, jenis, keterangan, kategori,
    jumlah, satuan, harga, total, catatan
):
    conn = get_connection()

    conn.execute("""
        INSERT INTO transaksi
        (tanggal, jenis, keterangan, kategori,
         jumlah, satuan, harga, total, catatan)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(tanggal), jenis, keterangan, kategori,
        jumlah, satuan, harga, total, catatan
    ))

    conn.commit()
    conn.close()

def ambil_data():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transaksi ORDER BY tanggal DESC, id DESC",
        conn
    )
    conn.close()
    return df

create_database()

# ==========================================
# FORMAT RUPIAH
# ==========================================

def rupiah(nilai):
    return "Rp " + f"{nilai:,.0f}".replace(",", ".")

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("💰 MY FINANCE")
st.sidebar.caption("Aplikasi pencatatan keuangan harian")

menu = st.sidebar.radio(
    "Pilih Menu",
    [
        "Dashboard",
        "Pembelian",
        "Pemasukan",
        "Pengeluaran Belanja",
        "Riwayat Transaksi"
    ]
)

df = ambil_data()

# ==========================================
# HITUNG SALDO
# ==========================================

total_pemasukan = df.loc[
    df["jenis"] == "Pemasukan", "total"
].sum()

total_pembelian = df.loc[
    df["jenis"] == "Pembelian", "total"
].sum()

total_pengeluaran = df.loc[
    df["jenis"] == "Pengeluaran", "total"
].sum()

total_keluar = total_pembelian + total_pengeluaran

saldo = total_pemasukan - total_keluar

# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.title("📊 Dashboard Keuangan")
    st.write("Ringkasan kondisi keuangan saat ini.")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Pemasukan",
        rupiah(total_pemasukan)
    )

    col2.metric(
        "Total Pengeluaran",
        rupiah(total_keluar)
    )

    col3.metric(
        "Saldo Saat Ini",
        rupiah(saldo),
        delta=None
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rincian Pengeluaran")

        rincian = pd.DataFrame({
            "Jenis": ["Pembelian", "Pengeluaran Belanja"],
            "Total": [total_pembelian, total_pengeluaran]
        })

        if rincian["Total"].sum() > 0:
            st.bar_chart(
                rincian.set_index("Jenis")
            )
        else:
            st.info("Belum ada pengeluaran.")

    with col2:
        st.subheader("Komposisi Keuangan")

        keuangan = pd.DataFrame({
            "Jenis": ["Pemasukan", "Pengeluaran"],
            "Total": [total_pemasukan, total_keluar]
        })

        if keuangan["Total"].sum() > 0:
            st.bar_chart(
                keuangan.set_index("Jenis")
            )
        else:
            st.info("Belum ada transaksi.")

    st.divider()

    st.subheader("Transaksi Terakhir")

    if not df.empty:
        tampil = df[[
            "tanggal", "jenis", "keterangan", "total"
        ]].head(10).copy()

        tampil.columns = [
            "Tanggal", "Jenis", "Keterangan", "Total"
        ]

        tampil["Total"] = tampil["Total"].apply(rupiah)

        st.dataframe(
            tampil,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Belum ada data transaksi.")

# ==========================================
# MENU PEMBELIAN
# ==========================================

elif menu == "Pembelian":

    st.title("🛒 Input Pembelian")
    st.write("Catat barang atau kebutuhan yang dibeli.")

    with st.form("form_pembelian"):

        tanggal = st.date_input(
            "Tanggal Pembelian",
            value=date.today()
        )

        nama_barang = st.text_input(
            "Nama Barang",
            placeholder="Contoh: Telur, Beras, Minyak"
        )

        col1, col2 = st.columns(2)

        with col1:
            kategori = st.selectbox(
                "Kategori Barang",
                [
                    "Bahan Makanan",
                    "Sembako",
                    "Minuman",
                    "Perlengkapan Rumah",
                    "Lainnya"
                ]
            )

            jumlah = st.number_input(
                "Jumlah",
                min_value=0.0,
                value=1.0,
                step=1.0
            )

            satuan = st.selectbox(
                "Satuan",
                ["Kg", "Gram", "Liter", "Pcs", "Bungkus", "Dus", "Lainnya"]
            )

        with col2:
            harga = st.number_input(
                "Harga per Satuan (Rp)",
                min_value=0,
                step=1000
            )

            total = jumlah * harga

            st.metric(
                "Total Pembelian",
                rupiah(total)
            )

        catatan = st.text_area("Catatan (Opsional)")

        submit = st.form_submit_button(
            "Simpan Pembelian",
            use_container_width=True
        )

        if submit:
            if not nama_barang.strip():
                st.error("Nama barang harus diisi.")
            elif jumlah <= 0 or harga <= 0:
                st.error("Jumlah dan harga harus lebih dari 0.")
            else:
                tambah_transaksi(
                    tanggal,
                    "Pembelian",
                    nama_barang,
                    kategori,
                    jumlah,
                    satuan,
                    harga,
                    total,
                    catatan
                )

                st.success("Pembelian berhasil disimpan!")
                st.rerun()

# ==========================================
# MENU PEMASUKAN
# ==========================================

elif menu == "Pemasukan":

    st.title("💵 Input Pemasukan")
    st.write("Catat semua uang yang masuk.")

    with st.form("form_pemasukan"):

        tanggal = st.date_input(
            "Tanggal Pemasukan",
            value=date.today()
        )

        sumber = st.text_input(
            "Sumber Pemasukan",
            placeholder="Contoh: Gaji, Penjualan, Bonus"
        )

        kategori = st.selectbox(
            "Kategori",
            [
                "Gaji",
                "Penjualan",
                "Bonus",
                "Transfer",
                "Hadiah",
                "Lainnya"
            ]
        )

        jumlah = st.number_input(
            "Nominal Pemasukan (Rp)",
            min_value=0,
            step=10000
        )

        catatan = st.text_area("Catatan (Opsional)")

        submit = st.form_submit_button(
            "Simpan Pemasukan",
            use_container_width=True
        )

        if submit:
            if not sumber.strip():
                st.error("Sumber pemasukan harus diisi.")
            elif jumlah <= 0:
                st.error("Nominal harus lebih dari 0.")
            else:
                tambah_transaksi(
                    tanggal,
                    "Pemasukan",
                    sumber,
                    kategori,
                    1,
                    "Transaksi",
                    jumlah,
                    jumlah,
                    catatan
                )

                st.success("Pemasukan berhasil disimpan!")
                st.rerun()

# ==========================================
# MENU PENGELUARAN BELANJA
# ==========================================

elif menu == "Pengeluaran Belanja":

    st.title("💸 Input Pengeluaran Belanja")
    st.write("Catat pengeluaran selain pembelian barang harian.")

    with st.form("form_pengeluaran"):

        tanggal = st.date_input(
            "Tanggal Pengeluaran",
            value=date.today()
        )

        keterangan = st.text_input(
            "Keterangan Pengeluaran",
            placeholder="Contoh: Bayar listrik, Air, Transportasi"
        )

        kategori = st.selectbox(
            "Kategori Pengeluaran",
            [
                "Listrik",
                "Air",
                "Transportasi",
                "Tagihan",
                "Kesehatan",
                "Pendidikan",
                "Rumah Tangga",
                "Lainnya"
            ]
        )

        jumlah = st.number_input(
            "Nominal Pengeluaran (Rp)",
            min_value=0,
            step=10000
        )

        catatan = st.text_area("Catatan (Opsional)")

        submit = st.form_submit_button(
            "Simpan Pengeluaran",
            use_container_width=True
        )

        if submit:
            if not keterangan.strip():
                st.error("Keterangan harus diisi.")
            elif jumlah <= 0:
                st.error("Nominal harus lebih dari 0.")
            else:
                tambah_transaksi(
                    tanggal,
                    "Pengeluaran",
                    keterangan,
                    kategori,
                    1,
                    "Transaksi",
                    jumlah,
                    jumlah,
                    catatan
                )

                st.success("Pengeluaran berhasil disimpan!")
                st.rerun()

# ==========================================
# RIWAYAT TRANSAKSI
# ==========================================

elif menu == "Riwayat Transaksi":

    st.title("📋 Riwayat Transaksi")
    st.write("Semua data pembelian, pemasukan, dan pengeluaran.")

    if not df.empty:

        jenis_filter = st.selectbox(
            "Filter Jenis Transaksi",
            [
                "Semua",
                "Pembelian",
                "Pemasukan",
                "Pengeluaran"
            ]
        )

        data = df.copy()

        if jenis_filter != "Semua":
            data = data[data["jenis"] == jenis_filter]

        data_tampil = data[[
            "id",
            "tanggal",
            "jenis",
            "keterangan",
            "kategori",
            "jumlah",
            "satuan",
            "harga",
            "total",
            "catatan"
        ]].copy()

        data_tampil.columns = [
            "ID",
            "Tanggal",
            "Jenis",
            "Keterangan",
            "Kategori",
            "Jumlah",
            "Satuan",
            "Harga Satuan",
            "Total",
            "Catatan"
        ]

        st.dataframe(
            data_tampil,
            use_container_width=True,
            hide_index=True
        )

        # Download data ke Excel
        excel_data = data_tampil.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "📥 Download Data CSV",
            data=excel_data,
            file_name="laporan_keuangan.csv",
            mime="text/csv"
        )

        st.divider()

        st.subheader("Hapus Transaksi")

        id_hapus = st.number_input(
            "Masukkan ID transaksi yang ingin dihapus",
            min_value=1,
            step=1
        )

        if st.button("🗑️ Hapus Transaksi"):
            conn = get_connection()

            cursor = conn.execute(
                "DELETE FROM transaksi WHERE id = ?",
                (int(id_hapus),)
            )

            conn.commit()
            berhasil = cursor.rowcount > 0
            conn.close()

            if berhasil:
                st.success("Transaksi berhasil dihapus.")
                st.rerun()
            else:
                st.error("ID transaksi tidak ditemukan.")

    else:
        st.info("Belum ada riwayat transaksi.")
