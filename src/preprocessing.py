import pandas as pd
import datetime as dt
import os

# Dizin yapılandırması
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "../data/raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "../data/processed")

# Çıktı klasörünü kontrol et
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def calculate_rfm(file_name, id_col, date_col, invoice_col, price_col=None, qty_col=None, sales_col=None, encoding="utf-8"):
    """
    Verilen veri setinden RFM metriklerini hesaplar ve temizlenmiş veriyi kaydeder.
    """
    file_path = os.path.join(RAW_DATA_DIR, file_name)
    
    if not os.path.exists(file_path):
        print(f"HATA: {file_name} bulunamadı. Lütfen data/raw içine yerleştirin.")
        return None

    print(f"--- {file_name} işleniyor ---")
    
    # Dosya uzantısına göre okuma motoru seçimi
    try:
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path, engine="openpyxl")
        elif file_path.endswith(".xls"):
            df = pd.read_excel(file_path, engine="xlrd")
        else:
            df = pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        print(f"Okuma hatası: {e}")
        return None

    # Veri Temizliği
    df.dropna(subset=[id_col], inplace=True)
    df["TransactionDate"] = pd.to_datetime(df[date_col]).dt.normalize()
    
    # Parasal Değer (Monetary) Hesaplama
    if sales_col:
        df["TotalAmount"] = df[sales_col]
    elif price_col and qty_col:
        # İptallerin temizlenmesi
        if invoice_col in df.columns:
            df = df[~df[invoice_col].astype(str).str.startswith('C')]
        df = df[(df[qty_col] > 0) & (df[price_col] > 0)]
        df["TotalAmount"] = df[qty_col] * df[price_col]

    # Analiz tarihi (Son işlem + 2 gün)
    ref_date = df["TransactionDate"].max() + dt.timedelta(days=2)

    # Gruplama
    rfm = df.groupby(id_col).agg({
        "TransactionDate": lambda date: (ref_date - date.max()).days,
        invoice_col: "nunique",
        "TotalAmount": "sum"
    }).reset_index()

    rfm.columns = [id_col, "Recency", "Frequency", "Monetary"]
    
    # Outlier temizliği (%99 quantile)
    rfm = rfm[rfm["Monetary"] > 0]
    for col in ["Recency", "Frequency", "Monetary"]:
        limit = rfm[col].quantile(0.99)
        rfm = rfm[rfm[col] < limit]

    # Yeni isimlendirme formatı: ebc_processed_[dosya_adi].csv
    clean_name = file_name.replace(" ", "_").split(".")[0].lower()
    output_name = f"ebc_processed_{clean_name}.csv"
    output_path = os.path.join(PROCESSED_DATA_DIR, output_name)
    
    rfm.to_csv(output_path, index=False)
    print(f"KAYDEDİLDİ: {output_path}")
    return rfm

if __name__ == "__main__":
   
    # Online Retail
    calculate_rfm(
        file_name="Online_Retail.xlsx", 
        id_col="CustomerID",
        date_col="InvoiceDate",
        invoice_col="InvoiceNo",
        price_col="UnitPrice",
        qty_col="Quantity",
        encoding="ISO-8859-1"
    )

    # Superstore 
    calculate_rfm(
        file_name="Superstore.csv",
        id_col="Customer ID",
        date_col="Order Date",
        invoice_col="Order ID",
        sales_col="Sales",
        encoding="windows-1252" 
    )