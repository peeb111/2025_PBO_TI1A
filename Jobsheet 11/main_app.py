""" # main_app.py
import streamlit as st
import datetime
import pandas as pd
import locale

# --- Pengaturan Locale (Opsional, untuk format mata uang) ---
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except:
        print("Locale id_ID/Indonesian tidak tersedia.")

def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except:
        return f"Rp {angka or 0:.0f}".replace(",", ".") # fallback jika locale gagal

# --- Import Modul Aplikasi ---
try:
    from model import Transaksi
    from manajer_anggaran import AnggaranHarian
    from konfigurasi import KATEGORI_PENGELUARAN # Ambil list kategori
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file .py lain ada.")
    st.stop()


# --- Inisialisasi Pengelola Anggaran (Gunakan Cache) ---
@st.cache_resource
def get_anggaran_manager():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi AnggaranHarian...")
    return AnggaranHarian() # Ini akan memicu cek DB/Tabel di __init__
anggaran = get_anggaran_manager()

# --- Fungsi Halaman/UI ---
def halaman_input(anggaran: AnggaranHarian):
    st.header("💸 Tambah Pengeluaran Baru")
    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            deskripsi = st.text_input("Deskripsi*",
                                       placeholder="Contoh: Makan siang")
        with col2:
            kategori = st.selectbox("Kategori*",
                                    KATEGORI_PENGELUARAN, index=0)

        col3, col4 = st.columns([1, 1]);
        with col3:
            jumlah = st.number_input("Jumlah (Rp)*:",
                                     min_value=0.0, step=1000.0, format="%.0f", value=None, placeholder="Contoh: 25000")
        with col4:
            tanggal = st.date_input("Tanggal*:",
                                   value=datetime.date.today())

        submitted = st.form_submit_button("💾 Simpan Transaksi");
        if submitted:
            if not deskripsi: st.warning("Deskripsi wajib!", icon="⚠️")
            elif jumlah is None or jumlah <= 0: st.warning("Jumlah wajib!", icon="⚠️")
            else:
                with st.spinner("Menyimpan..."):
                    tx = Transaksi(deskripsi, float(jumlah), kategori,
                                   tanggal)
                    if anggaran.tambah_transaksi(tx):
                        st.success(f"OK! Simpan.", icon="✅"); st.cache_data.clear(); st.rerun()
                    else:
                        st.error("Gagal simpan.", icon="❌")

def halaman_riwayat(anggaran: AnggaranHarian):
    st.subheader("Detail Semua Transaksi")
    if st.button("🔄 Refresh Riwayat"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data
    def get_df_transaksi():
        with st.spinner("Memuat riwayat..."):
            return anggaran.get_dataframe_transaksi()

    df_transaksi = get_df_transaksi()
    if df_transaksi.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(df_transaksi, use_container_width=True, hide_index=True)


def halaman_ringkasan(anggaran: AnggaranHarian):
    st.subheader("Ringkasan Pengeluaran")
    col_filter1, col_filter2 = st.columns([1, 2])
    with col_filter1:
        pilihan_periode = st.selectbox("Filter Periode:", ["Semua Waktu", "Hari Ini", "Pilih Tanggal"], key="filter_periode", on_change=lambda: st.cache_data.clear())
        tanggal_filter = None; label_periode = " (Semua Waktu)"

    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today(); label_periode = f"({tanggal_filter.strftime('%d %b')})"
    elif pilihan_periode == "Pilih Tanggal Tertentu":
        if 'tanggal_pilihan_state' not in st.session_state:
            st.session_state.tanggal_pilihan_state = datetime.date.today()
        tanggal_filter = st.date_input("Pilih Tanggal:",
                                       value=st.session_state.tanggal_pilihan_state,
                                       key="tanggal_pilihan",
                                       on_change= handle_tanggal_pilihan_change) # Ganti lambda dengan nama fungsi
        

    with col_filter2:
        @st.cache_data(ttl=300) # Cache hasil total
        def hitung_total_cached(tgl_filter):
            return anggaran.hitung_total_pengeluaran(tanggal=tgl_filter)
        total_pengeluaran = hitung_total_cached(tanggal_filter)
        st.metric(label=f"Total Pengeluaran {label_periode}", value=format_rp(total_pengeluaran))

    st.divider()
    st.subheader(f"Pengeluaran Per Kategori {label_periode}")
    @st.cache_data(ttl=300) # Cache hasil kategori
    def get_kategori_cached(tgl_filter): return anggaran.get_pengeluaran_per_kategori(tanggal=tgl_filter)
    with st.spinner("Memuat ringkasan kategori..."):
        dict_per_kategori = get_kategori_cached(tanggal_filter)

    if not dict_per_kategori:
        st.info("Tidak ada data untuk periode ini.")
    else:
        try:
            data_kategori = [{"Kategori": kat, "Total": jml} for kat, jml in dict_per_kategori.items()]
            df_kategori = pd.DataFrame(data_kategori).sort_values(by="Total", ascending=False).reset_index(drop=True)
            df_kategori['Total (Rp)'] = df_kategori['Total'].apply(format_rp)

            col_kat1, col_kat2 = st.columns(2)
            with col_kat1:
                st.write("Tabel:")
                st.dataframe(df_kategori[['Kategori', 'Total (Rp)']], hide_index=True, use_container_width=True)
            with col_kat2:
                st.write("Grafik:")
                st.bar_chart(df_kategori.set_index('Kategori')['Total'], use_container_width=True)
        except Exception as e:
            st.error(f"Gagal tampilkan ringkasan: {e}")

# --- Fungsi Utama Aplikasi Streamlit ---
def main():
    st.sidebar.title("💰 Catatan Pengeluaran")
    menu_pilihan = st.sidebar.radio("Pilih Menu:", ["Tambah", "Riwayat", "Ringkasan"], key="menu_utama")
    st.sidebar.markdown("---")
    st.sidebar.info("Jobsheet - Aplikasi Keuangan")

    manajer_anggaran = get_anggaran_manager()
    if menu_pilihan == "Tambah":
        halaman_input(manajer_anggaran)
    elif menu_pilihan == "Riwayat":
        halaman_riwayat(manajer_anggaran)
    elif menu_pilihan == "Ringkasan":
        halaman_ringkasan(manajer_anggaran)

    st.markdown("---"); st.caption("Pengembangan Aplikasi Berbasis OOP")


if __name__ == "__main__":
    main() # Jalankan fungsi utama"""

# main_app.py (diperbarui)
import streamlit as st
import datetime
import pandas as pd
import locale

# --- Pengaturan Locale (Opsional, untuk format mata uang) ---
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Indonesian_Indonesia.1252')
    except:
        print("Locale id_ID/Indonesian tidak tersedia.")

def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol='Rp ')[:-3]
    except:
        return f"Rp {angka or 0:.0f}".replace(",", ".") # fallback jika locale gagal

# --- Import Modul Aplikasi ---
try:
    from model import Transaksi
    from manajer_anggaran import AnggaranHarian
    from konfigurasi import KATEGORI_PENGELUARAN # Ambil list kategori
except ImportError as e:
    st.error(f"Gagal mengimpor modul: {e}. Pastikan file .py lain ada.")
    st.stop()


# --- Inisialisasi Pengelola Anggaran (Gunakan Cache) ---
@st.cache_resource
def get_anggaran_manager():
    print(">>> STREAMLIT: (Cache Resource) Menginisialisasi AnggaranHarian...")
    return AnggaranHarian() # Ini akan memicu cek DB/Tabel di __init__
anggaran = get_anggaran_manager()

# Fungsi untuk menangani perubahan pilihan tanggal di halaman ringkasan
def handle_tanggal_pilihan_change():
    # Hapus data cache saat pilihan tanggal berubah
    st.cache_data.clear()

# --- Fungsi Halaman/UI ---
def halaman_input(anggaran: AnggaranHarian):
    st.header("💸 Tambah Pengeluaran Baru")
    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            deskripsi = st.text_input("Deskripsi*",
                                       placeholder="Contoh: Makan siang")
        with col2:
            kategori = st.selectbox("Kategori*",
                                    KATEGORI_PENGELUARAN, index=0)

        col3, col4 = st.columns([1, 1]);
        with col3:
            jumlah = st.number_input("Jumlah (Rp)*:",
                                     min_value=0.0, step=1000.0, format="%.0f", value=None, placeholder="Contoh: 25000")
        with col4:
            tanggal = st.date_input("Tanggal*:",
                                   value=datetime.date.today())

        submitted = st.form_submit_button("💾 Simpan Transaksi");
        if submitted:
            if not deskripsi: st.warning("Deskripsi wajib!", icon="⚠️")
            elif jumlah is None or jumlah <= 0: st.warning("Jumlah wajib!", icon="⚠️")
            else:
                with st.spinner("Menyimpan..."):
                    tx = Transaksi(deskripsi, float(jumlah), kategori,
                                   tanggal)
                    if anggaran.tambah_transaksi(tx):
                        st.success(f"OK! Simpan.", icon="✅"); st.cache_data.clear(); st.rerun()
                    else:
                        st.error("Gagal simpan.", icon="❌")

def halaman_riwayat(anggaran: AnggaranHarian):
    st.subheader("Detail Semua Transaksi")
    if st.button("🔄 Refresh Riwayat"):
        st.cache_data.clear()
        st.rerun()

    @st.cache_data
    def get_df_transaksi():
        with st.spinner("Memuat riwayat..."):
            return anggaran.get_dataframe_transaksi()

    df_transaksi = get_df_transaksi()
    if df_transaksi.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(df_transaksi, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Hapus Transaksi")
        col_del1, col_del2 = st.columns([1, 2])
        with col_del1:
            # Dapatkan ID maksimum dari dataframe untuk min_value dan max_value
            max_id = df_transaksi['id'].max() if not df_transaksi.empty else 1
            id_to_delete = st.number_input("ID Transaksi untuk Dihapus:",
                                           min_value=1,
                                           max_value=int(max_id), # Pastikan max_value adalah int
                                           step=1,
                                           value=1, # Nilai default
                                           key="id_delete_input")
        with col_del2:
            st.write("") # Spasi
            st.write("") # Spasi
            if st.button("🗑️ Hapus Transaksi Terpilih", key="delete_button"):
                st.session_state.confirm_delete = True # Atur status sesi untuk konfirmasi

        if st.session_state.get('confirm_delete', False):
            st.warning(f"Anda yakin ingin menghapus transaksi dengan ID: **{id_to_delete}**?", icon="⚠️")
            col_confirm1, col_confirm2 = st.columns(2)
            with col_confirm1:
                if st.button("✅ Konfirmasi Hapus", key="confirm_delete_yes"):
                    with st.spinner(f"Menghapus transaksi ID {id_to_delete}..."):
                        if anggaran.hapus_transaksi(int(id_to_delete)):
                            st.success(f"Transaksi ID {id_to_delete} berhasil dihapus.", icon="✅")
                            st.cache_data.clear() # Bersihkan cache untuk memuat ulang data
                            st.session_state.confirm_delete = False # Reset status konfirmasi
                            st.rerun() # Muat ulang untuk memperbarui tampilan
                        else:
                            st.error(f"Gagal menghapus transaksi ID {id_to_delete}.", icon="❌")
                            st.session_state.confirm_delete = False # Reset status konfirmasi
            with col_confirm2:
                if st.button("❌ Batal", key="confirm_delete_no"):
                    st.session_state.confirm_delete = False # Reset status konfirmasi
                    st.info("Penghapusan dibatalkan.")
                    st.rerun() # Muat ulang untuk menghapus pesan konfirmasi


def halaman_ringkasan(anggaran: AnggaranHarian):
    st.subheader("Ringkasan Pengeluaran")
    col_filter1, col_filter2 = st.columns([1, 2])
    with col_filter1:
        pilihan_periode = st.selectbox("Filter Periode:", ["Semua Waktu", "Hari Ini", "Pilih Tanggal"], key="filter_periode", on_change=lambda: st.cache_data.clear())
        tanggal_filter = None; label_periode = " (Semua Waktu)"

    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today(); label_periode = f"({tanggal_filter.strftime('%d %b')})"
    elif pilihan_periode == "Pilih Tanggal": # Mengubah dari "Pilih Tanggal Tertentu"
        if 'tanggal_pilihan_state' not in st.session_state:
            st.session_state.tanggal_pilihan_state = datetime.date.today()
        tanggal_filter = st.date_input("Pilih Tanggal:",
                                       value=st.session_state.tanggal_pilihan_state,
                                       key="tanggal_pilihan",
                                       on_change= handle_tanggal_pilihan_change) # Mengganti lambda dengan nama fungsi


    with col_filter2:
        @st.cache_data(ttl=300) # Cache hasil total
        def hitung_total_cached(tgl_filter):
            return anggaran.hitung_total_pengeluaran(tanggal=tgl_filter)
        total_pengeluaran = hitung_total_cached(tanggal_filter)
        st.metric(label=f"Total Pengeluaran {label_periode}", value=format_rp(total_pengeluaran))

    st.divider()
    st.subheader(f"Pengeluaran Per Kategori {label_periode}")
    @st.cache_data(ttl=300) # Cache hasil kategori
    def get_kategori_cached(tgl_filter): return anggaran.get_pengeluaran_per_kategori(tanggal=tgl_filter)
    with st.spinner("Memuat ringkasan kategori..."):
        dict_per_kategori = get_kategori_cached(tanggal_filter)

    if not dict_per_kategori:
        st.info("Tidak ada data untuk periode ini.")
    else:
        try:
            data_kategori = [{"Kategori": kat, "Total": jml} for kat, jml in dict_per_kategori.items()]
            df_kategori = pd.DataFrame(data_kategori).sort_values(by="Total", ascending=False).reset_index(drop=True)
            df_kategori['Total (Rp)'] = df_kategori['Total'].apply(format_rp)

            col_kat1, col_kat2 = st.columns(2)
            with col_kat1:
                st.write("Tabel:")
                st.dataframe(df_kategori[['Kategori', 'Total (Rp)']], hide_index=True, use_container_width=True)
            with col_kat2:
                st.write("Grafik:")
                st.bar_chart(df_kategori.set_index('Kategori')['Total'], use_container_width=True)
        except Exception as e:
            st.error(f"Gagal tampilkan ringkasan: {e}")

# --- Fungsi Utama Aplikasi Streamlit ---
def main():
    st.sidebar.title("💰 Catatan Pengeluaran")
    menu_pilihan = st.sidebar.radio("Pilih Menu:", ["Tambah", "Riwayat", "Ringkasan"], key="menu_utama")
    st.sidebar.markdown("---")
    st.sidebar.info("Jobsheet - Aplikasi Keuangan")

    manajer_anggaran = get_anggaran_manager()
    if menu_pilihan == "Tambah":
        halaman_input(manajer_anggaran)
    elif menu_pilihan == "Riwayat":
        halaman_riwayat(manajer_anggaran)
    elif menu_pilihan == "Ringkasan":
        halaman_ringkasan(manajer_anggaran)

    st.markdown("---"); st.caption("Pengembangan Aplikasi Berbasis OOP")


if __name__ == "__main__":
    main() # Jalankan fungsi utama