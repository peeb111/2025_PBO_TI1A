import pandas as pd
from abc import ABC, abstractmethod # Diperlukan untuk definisi kelas

# --- Definisi Kelas (Salin dari Praktikum 3) ---
class Lokasi(ABC):
    def __init__(self, nama: str, latitude: float, longitude: float):
        self.nama = str(nama) if nama else "Tanpa Nama"
        try:
            self.latitude = float(latitude)
            self.longitude = float(longitude)
        except (ValueError, TypeError, SystemError):
            # print(f"  -> Peringatan: Koordinat tidak valid untuk '{self.nama}'. Set ke (0.0, 0.0).")
            self.latitude = 0.0
            self.longitude = 0.0

    def get_koordinat(self) -> tuple:
        return (self.latitude, self.longitude)

    @abstractmethod
    def get_info_popup(self) -> str:
        pass

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nama='{self.nama}', lat={self.latitude:.4f}, lon={self.longitude:.4f})"

    def __str__(self) -> str:
        return f"{self.nama} [{type(self).__name__}]"


class TempatWisata(Lokasi):
    def __init__(self, nama: str, latitude: float, longitude: float,
                 jenis: str, deskripsi: str):
        super().__init__(nama, latitude, longitude)
        self.jenis_wisata = str(jenis) if jenis else "Umum"
        self.deskripsi = str(deskripsi) if deskripsi else "Tidak ada deskripsi."

    def get_info_popup(self) -> str:
        # Mengganti baris baru dengan <br> untuk HTML
        return f"<h4><b>{self.nama}</b></h4><i>{self.jenis_wisata}</i><br>{self.deskripsi}<br>Koordinat: ({self.latitude:.4f}, {self.longitude:.4f})"


class Kuliner(Lokasi):
    def __init__(self, nama: str, latitude: float, longitude: float,
                 menu_andalan: str):
        super().__init__(nama, latitude, longitude)
        self.menu_andalan = str(menu_andalan) if menu_andalan else "Tidak diketahui"

    def get_info_popup(self) -> str:
        # Mengganti baris baru dengan <br> untuk HTML
        return f"{self.nama}<br>Kuliner<br><br>Menu Andalan: {self.menu_andalan}<br><br>Koordinat: ({self.latitude:.4f}, {self.longitude:.4f})"


class TempatIbadah(Lokasi):
    def __init__(self, nama: str, latitude: float, longitude: float,
                 agama: str = "Umum", deskripsi: str = ""):
        super().__init__(nama, latitude, longitude)
        self.agama = str(agama) if agama else "Umum"
        self.deskripsi = str(deskripsi) if deskripsi else "Tempat Ibadah" # Perbaikan indentasi dan penempatan

    def get_info_popup(self) -> str:
        # Mengganti baris baru dengan <br> untuk HTML
        return f"{self.nama}<br>Tempat Ibadah ({self.agama})<br><br>{self.deskripsi}<br><br>Koordinat: ({self.latitude:.4f}, {self.longitude:.4f})"


# --- Fungsi baca data (Salin dari Praktikum 2) ---
def baca_data_lokasi(nama_file: str) -> pd.DataFrame | None:
    # print(f"Mencoba membaca file CSV: {nama_file}") # Kurangi verbosity
    try:
        dataframe = pd.read_csv(nama_file)
        return dataframe
    except FileNotFoundError:
        print(f"ERROR: File '{nama_file}' tidak ditemukan!");
        return None
    except Exception as e:
        print(f"ERROR saat membaca file CSV: {type(e).__name__} - {e}");
        return None


# --- Fungsi Inti Praktikum Ini ---
def buat_objek_lokasi_dari_df(dataframe: pd.DataFrame) -> list:
    """
    Mengiterasi DataFrame Pandas dan membuat list berisi objek-objek
    Lokasi (atau turunannya) berdasarkan data di setiap baris.

    Args:
        dataframe (pd.DataFrame): DataFrame yang berisi data lokasi
                                  dengan kolom 'Nama', 'Latitude',
                                  'Longitude', 'Tipe', 'Deskripsi'.

    Returns:
        list: List berisi instance objek Lokasi atau turunannya.
    """
    list_objek_lokasi = []
    if dataframe is None or dataframe.empty:
        print("DataFrame kosong atau None, tidak ada objek dibuat.")
        return list_objek_lokasi

    print("\nMembuat objek dari DataFrame...")
    # Iterasi setiap baris dalam DataFrame
    for index, row in dataframe.iterrows():
        # Ambil data dari setiap kolom di baris saat ini
        # Gunakan .get() dengan default value untuk antisipasi kolom hilang
        nama = row.get('Nama', None)
        lat = row.get('Latitude', None)
        lon = row.get('Longitude', None)
        tipe = row.get('Tipe', 'Lainnya') # Default jika kolom Tipe tidak ada
        deskripsi = row.get('Deskripsi', '') # Default string kosong

        objek = None
        # Lakukan pengecekan tipe data dasar sebelum membuat objek
        if nama is None or lat is None or lon is None:
            print(f"  -> Melewati baris {index}: Data Nama/Latitude/Longitude tidak lengkap.")
            continue # Lanjut ke baris berikutnya

        # Membuat objek berdasarkan nilai di kolom 'Tipe'
        try:
            if 'Wisata' in tipe or tipe == 'Landmark':
                objek = TempatWisata(nama, lat, lon, tipe, deskripsi)
            elif tipe == 'Kuliner':
                # Menggunakan kolom 'Deskripsi' sebagai 'menu_andalan' untuk contoh ini
                # Perhatian: Kelas Kuliner yang didefinisikan tidak secara eksplisit menerima 'deskripsi'
                # sebagai parameter langsung ke atribut self.deskripsi.
                # Jika 'deskripsi' dari CSV ingin disimpan di Kuliner, perlu penyesuaian di __init__ Kuliner.
                objek = Kuliner(nama, lat, lon, deskripsi)
            elif 'Ibadah' in tipe:
                # Bisa ekstrak info agama dari tipe jika ada, atau set default
                agama_info = "Umum" # Default
                if "Islam" in tipe: agama_info="Islam"
                elif "Kristen" in tipe: agama_info="Kristen"
                elif "Klenteng" in tipe: agama_info="Tridharma"
                # Dst...
                objek = TempatIbadah(nama, lat, lon, agama_info, deskripsi)
            else:
                print(f"  -> Peringatan: Tipe '{tipe}' untuk '{nama}' tidak dikenali. Tidak membuat objek spesifik.")
                # Karena Lokasi abstrak, kita tidak bisa membuat objek Lokasi generik.
                # Jika Lokasi tidak abstrak, bisa: objek = Lokasi(nama, lat, lon)

            if objek:
                list_objek_lokasi.append(objek)
                # print(f"  -> Objek {type(objek).__name__} untuk '{nama}' dibuat.")

        except Exception as e:
            # Tangani error saat pembuatan objek (misal konversi tipe gagal di __init__)
            print(f"  -> GAGAL membuat objek untuk '{nama}' di baris {index}: {e}")

    print(f"Total {len(list_objek_lokasi)} objek lokasi berhasil dibuat dari {len(dataframe)} baris data.")
    return list_objek_lokasi

# --- Kode Utama ---
if __name__ == "__main__":
    NAMA_FILE_CSV = "Job12\lokasi_semarang.csv"

    print("--- Memulai Praktikum 4: Membuat Objek dari Data Pandas ---")
    # 1. Baca data CSV
    df_lokasi = baca_data_lokasi(NAMA_FILE_CSV)

    # 2. Buat list objek dari DataFrame
    list_semua_lokasi = buat_objek_lokasi_dari_df(df_lokasi)

    # 3. Tampilkan hasil (representasi objek)
    print("\n--- Daftar Objek Lokasi yang Berhasil Dibuat ---")
    if list_semua_lokasi:
        for idx, lok in enumerate(list_semua_lokasi):
            # repr() akan menunjukkan tipe objeknya (TempatWisata, Kuliner, dll.)
            print(f"{idx+1}. {repr(lok)}")
    else:
        print("Tidak ada objek lokasi yang dibuat.")

    print("\n--- Praktikum 4 Selesai ---")