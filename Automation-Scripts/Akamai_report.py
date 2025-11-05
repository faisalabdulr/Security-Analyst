import pandas as pd
import io
import tkinter as tk
from tkinter import filedialog

# ---------------- Utilitas Bersih Data ----------------
def clean_number(value):
    """
    Membersihkan format angka seperti ="123" -> 123
    """
    if pd.isna(value):
        return value
    val = str(value).replace('="', "").replace('"', "").strip()
    try:
        return int(val)
    except ValueError:
        return val


# ---------------- Bot Report ----------------
def report_bot(file_path):
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        if "Bot Category" in line:
            header_idx = i
            break
    if header_idx is None:
        return ["❌ Header 'Bot Category' tidak ditemukan"]

    sep = "\t" if "\t" in lines[header_idx] else ","
    df = pd.read_csv(io.StringIO("".join(lines[header_idx:])), sep=sep)

    # Bersihkan angka
    df.iloc[:, -1] = df.iloc[:, -1].apply(clean_number)

    max_len = df.iloc[:, 0].astype(str).str.len().max()
    output_lines = ["Monitoring jumlah bot request selama periode pemantauan :"]
    for _, row in df.iterrows():
        kategori = str(row.iloc[0]).ljust(max_len)
        jumlah = row.iloc[-1]
        output_lines.append(f"- {kategori} : {jumlah}")

    return output_lines


import pycountry

# ---------------- Country Report ----------------
def report_country(file_path):
    def get_country_name(code):
        try:
            country = pycountry.countries.get(alpha_2=code.strip().upper())
            return country.name if country else code
        except:
            return code

    with open(file_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        if "Country" in line or "Area" in line:
            header_idx = i
            break
    if header_idx is None:
        return ["❌ Header 'Country/Area' tidak ditemukan"]

    sep = "\t" if "\t" in lines[header_idx] else ","
    df = pd.read_csv(io.StringIO("".join(lines[header_idx:])), sep=sep)

    # Bersihkan angka
    df.iloc[:, -1] = df.iloc[:, -1].apply(clean_number)

    # Ambil Top 5
    df_top5 = df.head(5)

    # Mapping otomatis ke nama negara lengkap
    df_top5.iloc[:, 0] = df_top5.iloc[:, 0].apply(get_country_name)

    max_len = df_top5.iloc[:, 0].astype(str).str.len().max()

    output_lines = ["", "Monitoring Top 5 negara dengan percobaan akses terbanyak dengan Action Deny:"]
    for _, row in df_top5.iterrows():
        negara = str(row.iloc[0]).ljust(max_len)
        jumlah = row.iloc[-1]
        output_lines.append(f"⦁ {negara} : {jumlah}")

    return output_lines



# ---------------- WAF Report ----------------
def report_waf(file_path):
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_idx = None
    for i, line in enumerate(lines):
        if "Hostname" in line:
            header_idx = i
            break
    if header_idx is None:
        return ["❌ Header 'Hostname' tidak ditemukan"]

    sep = "\t" if "\t" in lines[header_idx] else ","
    df = pd.read_csv(io.StringIO("".join(lines[header_idx:])), sep=sep)

    # Bersihkan hostname
    df.iloc[:, 0] = (
        df.iloc[:, 0]
        .astype(str)
        .str.replace(".ptsmi.co.id", "", regex=False)
        .str.strip()
    )

    # Bersihkan angka
    df.iloc[:, -1] = df.iloc[:, -1].apply(clean_number)

    max_len = df.iloc[:, 0].astype(str).str.len().max()

    output_lines = ["", "Monitoring Jumlah Block Request pada WAF Akamai:"]
    for _, row in df.iterrows():
        hostname = str(row.iloc[0]).ljust(max_len)
        jumlah = row.iloc[-1]
        output_lines.append(f"{hostname} : {jumlah}")

    return output_lines


# ---------------- Main ----------------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    print("Pilih file Bot Category (CSV)...")
    bot_file = filedialog.askopenfilename(title="Pilih file Bot Category (CSV)", filetypes=[("CSV files", "*.csv")])

    print("Pilih file Country (CSV)...")
    country_file = filedialog.askopenfilename(title="Pilih file Country (CSV)", filetypes=[("CSV files", "*.csv")])

    print("Pilih file WAF (CSV)...")
    waf_file = filedialog.askopenfilename(title="Pilih file WAF (CSV)", filetypes=[("CSV files", "*.csv")])

    if not bot_file or not country_file or not waf_file:
        print("❌ Ada file yang tidak dipilih. Program dihentikan.")
    else:
        results = []
        results.extend(report_bot(bot_file))
        results.extend(report_country(country_file))
        results.extend(report_waf(waf_file))

        save_path = filedialog.asksaveasfilename(
            title="Simpan hasil laporan",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                for line in results:
                    f.write(line + "\n")
            print(f"✅ Hasil sudah ditulis ke {save_path}")
        else:
            print("❌ Penyimpanan dibatalkan.")
