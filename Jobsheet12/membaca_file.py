# Impor library pandas
import pandas as pd

# Nama file CSV yang akan dibaca
NAMA_FILE_CSV = "Job12/lokasi_semarang.csv"

def baca_data_lokasi(nama_file: str) -> pd.DataFrame | None:
    """
    Membaca data lokasi dari file CSV menggunakan Pandas.

    Args:
        nama_file (str): Path atau nama file CSV yang akan dibaca.

    Returns:
        pd.DataFrame | None: DataFrame Pandas berisi data jika berhasil,
        None jika file tidak ditemukan, kosong, atau error lain.
    """
    print(f"Mencoba membaca file CSV: {nama_file}")
    try:
        # Menggunakan pandas.read_csv untuk membaca file
        # Secara default, read_csv menganggap baris pertama sebagai header
        # dan koma sebagai pemisah (separator).
        dataframe = pd.read_csv(nama_file)
        print(" -> File CSV berhasil dibaca.")
        return dataframe
    except FileNotFoundError:
        # Menangani jika file tidak ditemukan
        print(f" -> ERROR: File '{nama_file}' tidak ditemukan!")
        return None
    except pd.errors.EmptyDataError:
        # Menangani jika file kosong
        print(f" -> ERROR: File '{nama_file}' kosong.")
        return None
    except Exception as e:
        # Menangani error umum lainnya saat membaca CSV
        print(f" -> ERROR saat membaca file CSV: {type(e).__name__} - {e}")
        return None

# --- Kode Utama ---
if __name__ == "__main__":
    print("--- Memulai Praktikum 2: Membaca CSV ---")
    # Panggil fungsi untuk membaca data
    df_lokasi = baca_data_lokasi(NAMA_FILE_CSV)

    # Periksa apakah pembacaan berhasil (df_lokasi bukan None)
    if df_lokasi is not None:
        print("\n--- Inspeksi Awal DataFrame ---")

        # 1. Tampilkan 5 baris pertama data menggunakan head()
        print("\n1. Lima Baris Pertama (head()):")
        print(df_lokasi.head())

        # 2. Tampilkan informasi ringkas tentang DataFrame menggunakan info()
        #    (Jumlah baris, nama kolom, tipe data kolom, memori)
        print("\n2. Informasi DataFrame (info()):")
        df_lokasi.info()

        # 3. Tampilkan dimensi DataFrame (jumlah baris, jumlah kolom)
        jumlah_baris, jumlah_kolom = df_lokasi.shape
        print(f"\n3. Dimensi Data:")
        print(f"   Jumlah Lokasi (Baris) : {jumlah_baris}")
        print(f"   Jumlah Atribut (Kolom): {jumlah_kolom}")

        # 4. Tampilkan nama-nama kolom
        print(f"\n4. Nama Kolom:")
        print(list(df_lokasi.columns))
    else:
        print("\nTidak dapat melanjutkan inspeksi karena gagal membaca file CSV.")

    print("\n--- Praktikum 2 Selesai ---")