import pandas as pd
import numpy as np
import os
import json
import random
import uuid
from my_lib import ManualKMeans

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "../data/processed")
CONFIG_PATH = os.path.join(BASE_DIR, "../parameters.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "../data") # Final raporları data köküne atalım

def generate_marketing_campaign(segment):
    """Segment bazlı dinamik kampanya üreticisi."""
    segment = str(segment).lower()
    
    campaigns = {
        "champions": {
            "rate": 0.10,
            "prefix": "VIP10",
            "messages": ["👑 Sadece Size Özel VIP Ayrıcalığı!", "💎 Prestij Paketi: İndirimden fazlası."]
        },
        "loyal": {
            "rate": 0.15,
            "prefix": "SADIK15",
            "messages": ["🤝 Dostluğumuz Bakidir! İstikrarlı alışverişleriniz için.", "❤️ Sadakatiniz için %15 ödülünüz hazır."]
        },
        "risk": {
            "rate": 0.30,
            "prefix": "DON30",
            "messages": ["😔 Sizi Özledik! Geri dönmeniz şerefine dev indirim.", "🛑 Durun Gitmeyin! %30 fırsatını kaçırmayın."]
        },
        "potential": {
            "rate": 0.20,
            "prefix": "HOSGELDIN20",
            "messages": ["🚀 Maceraya Hazır Mısın? İkinci siparişine özel.", "🌱 İlk adımı attın, ikincisi bizden olsun."]
        }
    }
    
    # Segment eşleştirme mantığı
    selected_campaign = None
    if "champion" in segment or "şampiyon" in segment:
        selected_campaign = campaigns["champions"]
    elif "risk" in segment or "hibernating" in segment:
        selected_campaign = campaigns["risk"]
    elif "loyal" in segment or "sadık" in segment:
        selected_campaign = campaigns["loyal"]
    elif "potential" in segment or "new" in segment:
        selected_campaign = campaigns["potential"]
    else:
        selected_campaign = {"rate": 0.05, "prefix": "FIRSAT5", "messages": ["👋 Merhaba! Günün fırsatları."]}

    code = f"{selected_campaign['prefix']}-{str(uuid.uuid4())[:4].upper()}"
    return selected_campaign['rate'], code, random.choice(selected_campaign['messages'])

def execute_clustering_pipeline():
    if not os.path.exists(CONFIG_PATH):
        print("HATA: parameters.json bulunamadı. Önce evaluation.py çalıştırılmalı.")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        params = json.load(f)

    files = [f for f in os.listdir(PROCESSED_DIR) if f.startswith("ebc_processed_") and f.endswith(".csv")]
    
    for file in files:
        dataset_name = file.replace("ebc_processed_", "").replace(".csv", "")
        print(f"\n[MODELLEME] {dataset_name.upper()}")
        
        if dataset_name not in params:
            print(f"Uyarı: {dataset_name} için K değeri bulunamadı, atlanıyor.")
            continue
            
        k_val = params[dataset_name]["optimal_k"]
        print(f"Kullanılan K Değeri: {k_val}")
        
        file_path = os.path.join(PROCESSED_DIR, file)
        df = pd.read_csv(file_path, index_col=0)
        
        X_log = np.log1p(df).values
        X_scaled = (X_log - X_log.mean(axis=0)) / X_log.std(axis=0)
        
        model = ManualKMeans(n_clusters=k_val, init='k-means++', random_state=42)
        model.fit(X_scaled)
        
        df["Cluster_ID"] = model.labels
        
        # Küme Profilleme ve Skorlama
        cluster_summary = df.groupby("Cluster_ID").agg({
            "Recency": "mean", "Frequency": "mean", "Monetary": "mean"
        }).reset_index()
        
        # Basit RFM Skorlaması (R ters orantılı, F ve M doğru orantılı)
        cluster_summary["R_Score"] = 1 - ((cluster_summary["Recency"] - cluster_summary["Recency"].min()) / (cluster_summary["Recency"].max() - cluster_summary["Recency"].min() + 1e-9))
        cluster_summary["F_Score"] = (cluster_summary["Frequency"] - cluster_summary["Frequency"].min()) / (cluster_summary["Frequency"].max() - cluster_summary["Frequency"].min() + 1e-9)
        cluster_summary["M_Score"] = (cluster_summary["Monetary"] - cluster_summary["Monetary"].min()) / (cluster_summary["Monetary"].max() - cluster_summary["Monetary"].min() + 1e-9)
        cluster_summary["Total_Score"] = cluster_summary["R_Score"] + cluster_summary["F_Score"] + cluster_summary["M_Score"]
        
        cluster_summary = cluster_summary.sort_values("Total_Score", ascending=False)
        
        # Dinamik İsimlendirme
        labels = ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Hibernating"]
        # Elimizdeki küme sayısı kadar etiketi en üstten en alta doğru eşleştir
        mapped_labels = labels[:k_val-1] + [labels[-1]] if k_val < len(labels) else labels[:k_val]
        
        label_dict = {row["Cluster_ID"]: mapped_labels[i] for i, (_, row) in enumerate(cluster_summary.iterrows())}
        df["Segment"] = df["Cluster_ID"].map(label_dict)
        
        # Aksiyon Planı Üretimi
        df[["Discount_Rate", "Coupon_Code", "Message"]] = df.apply(lambda row: pd.Series(generate_marketing_campaign(row["Segment"])), axis=1)
        
        # Kayıt İşlemleri
        output_file = os.path.join(OUTPUT_DIR, f"Final_Action_Plan_{dataset_name}.xlsx")
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Customer_List")
            
            # Yönetici Özeti
            exec_summary = df.groupby("Segment").agg({
                "Recency": "mean", "Frequency": "mean", "Monetary": "mean", "Discount_Rate": "count"
            }).rename(columns={"Discount_Rate": "Customer_Count"}).round(2)
            exec_summary.to_excel(writer, sheet_name="Executive_Summary")
            
        print(f"BAŞARILI: Aksiyon planı üretildi -> {output_file}")

if __name__ == "__main__":
    execute_clustering_pipeline()