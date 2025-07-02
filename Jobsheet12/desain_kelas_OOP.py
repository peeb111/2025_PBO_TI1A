class Buku:
    def __init__(self, judul, penulis, tahun, jml_halaman):
        self.judul = judul
        self.penulis = penulis
        self.tahun = tahun
        self.jml_halaman = max(0, jml_halaman) # Pastikan non-negatif

    def __str__(self):
        # Versi singkat untuk kejelasan perbandingan
        return f"'{self.judul}' ({self.tahun})"

    def __repr__(self):
        return f"Buku(judul='{self.judul}', penulis='{self.penulis}', tahun={self.tahun}, jml_halaman={self.jml_halaman})"

    def __len__(self):
        return self.jml_halaman

    # --- Implementasi Perbandingan ---

    # __eq__: Dipanggil saat menggunakan operator ==
    def __eq__(self, other):
        """Membandingkan kesamaan dua objek Buku berdasarkan judul dan penulis."""
        print(f"-> Memanggil __eq__: Membandingkan '{self.judul}' == '{getattr(other, 'judul', '?')}'")
        # Cek apakah 'other' adalah instance dari kelas Buku
        if isinstance(other, Buku):
            # Logika kesamaan: judul DAN penulis harus sama
            return (self.judul == other.judul) and (self.penulis == other.penulis)
        # Jika tipe berbeda, kembalikan NotImplemented agar Python bisa coba cara lain
        # atau menghasilkan TypeError jika tidak ada cara lain.
        return NotImplemented

    # __lt__: Dipanggil saat menggunakan operator <
    def __lt__(self, other):
        """Membandingkan objek Buku berdasarkan tahun terbit (lebih kecil dari)."""
        print(f"-> Memanggil __lt__: Membandingkan '{self.judul}' ({self.tahun}) < '{getattr(other, 'judul', '?')}' ({getattr(other, 'tahun', '?')})")
        # Cek apakah 'other' adalah instance dari kelas Buku
        if isinstance(other, Buku):
            # Logika perbandingan: bandingkan tahun terbit
            return self.tahun < other.tahun
        # Jika tipe berbeda, operasi tidak didukung
        return NotImplemented

    # Catatan: Jika Anda implementasi __eq__ dan __lt__, Python seringkali
    # bisa secara otomatis menyediakan implementasi untuk __ne__, __gt__,
    # __le__, __ge__ berdasarkan logika __eq__ dan __lt__.
    # Namun, untuk kontrol penuh atau optimasi, Anda bisa implementasikan
    # semuanya secara eksplisit jika perlu.

# --- Kode Utama ---
if __name__ == "__main__":
    buku_A = Buku("Sejarah Jawa Kuno", "Prof. X", 1995, 450)
    buku_B = Buku("Teknologi AI", "Dr. Y", 2022, 300)
    buku_C = Buku("Sejarah Jawa Kuno", "Prof. X", 1995, 500) # Sama judul&penulis dgn A
    buku_D = Buku("Pengantar Python", "Prof. X", 2018, 400)

    print("\n--- Perbandingan Kesamaan (==) ---")
    print(f"'{buku_A.judul}' == '{buku_B.judul}' ? {buku_A == buku_B}") # False (beda judul/penulis)
    print(f"'{buku_A.judul}' == '{buku_C.judul}' ? {buku_A == buku_C}") # True (judul/penulis sama)
    print(f"'{buku_A.judul}' == 'Teks' ? {buku_A == 'Teks'}")       # False (beda tipe)

    print("\n--- Perbandingan Kurang Dari (<) ---")
    print(f"{buku_A} < {buku_B} ? {buku_A < buku_B}") # True (1995 < 2022)
    print(f"{buku_B} < {buku_A} ? {buku_B < buku_A}") # False (2022 > 1995)
    print(f"{buku_A} < {buku_C} ? {buku_A < buku_C}") # False (1995 == 1995)
    print(f"{buku_A} < {buku_D} ? {buku_A < buku_D}") # True (1995 < 2018)

    print("\n--- Perbandingan Lain (Otomatis dari __lt__ dan __eq__) ---")
    # Python menggunakan __lt__ dan __eq__ untuk menurunkan perbandingan lain
    print(f"{buku_B} > {buku_A} ? {buku_B > buku_A}")   # True (kebalikan <)
    print(f"{buku_A} != {buku_B} ? {buku_A != buku_B}") # True (kebalikan ==)

    print("\n--- Perbandingan dengan Tipe Lain ---")
    try:
        # Ini akan memanggil buku_A.__lt__(5), yang mengembalikan NotImplemented
        # Python lalu mencoba 5.__gt__(buku_A), juga gagal -> TypeError
        hasil_error = buku_A < 5
        print(f"Hasil buku_A < 5 : {hasil_error}")
    except TypeError as e:
        print(f"Error saat membandingkan buku_A < 5: {e}")