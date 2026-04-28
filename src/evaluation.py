import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
from my_lib import ManualKMeans

# Dizin mimarisi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "../data/processed")
DOCS_DIR = os.path.join(BASE_DIR, "../docs")
CONFIG_PATH = os.path.join(BASE_DIR, "../parameters.json")

# Dokümantasyon klasörünü garantiye al
os.makedirs(DOCS_DIR, exist_ok=True)

def euclidean_distances(X):
    """
    Vektörize edilmiş, bellek dostu Öklid uzaklık matrisi hesabı.
    (MemoryError almamak için for döngüsü yerine matris çarpımı kullanılır.)
    """
    sq_sum = np.sum(np.square(X), axis=1)
    dists = -2 * np.dot(X, X.T) + sq_sum[:, np.newaxis] + sq_sum
    return np.sqrt(np.maximum(dists, 0))

def calculate_silhouette(X, labels, dist_matrix):
    """Optimize edilmiş Silhouette Skoru hesaplaması."""
    n_samples = len(X)
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2:
        return -1.0
        
    silhouettes = np.zeros(n_samples)
    for i in range(n_samples):
        cluster = labels[i]
        mask_same = (labels == cluster)
        
        # a(i): Aynı kümedeki diğer noktalara ortalama uzaklık
        if np.sum(mask_same) > 1:
            a_i = np.sum(dist_matrix[i, mask_same]) / (np.sum(mask_same) - 1)
        else:
            a_i = 0
            
        # b(i): En yakın diğer kümeye olan ortalama uzaklık
        b_i = np.inf
        for other_cluster in unique_labels:
            if other_cluster == cluster:
                continue
            mask_other = (labels == other_cluster)
            mean_dist = np.mean(dist_matrix[i, mask_other])
            if mean_dist < b_i:
                b_i = mean_dist
                
        silhouettes[i] = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0
        
    return np.mean(silhouettes)

def evaluate_models():
    files = [f for f in os.listdir(PROCESSED_DIR) if f.startswith("ebc_processed_") and f.endswith(".csv")]
    if not files:
        print("HATA: data/processed dizininde işlenecek ebc_processed_*.csv dosyası bulunamadı.")
        return
        
    project_params = {}
    
    for file in files:
        dataset_name = file.replace("ebc_processed_", "").replace(".csv", "")
        file_path = os.path.join(PROCESSED_DIR, file)
        print(f"\n[ANALİZ BAŞLADI] {dataset_name.upper()}")
        
        df = pd.read_csv(file_path, index_col=0)
        
        # Veri Dönüşümü (Log Transformation & Standardization)
        log_data = np.log1p(df).values
        scaled_data = (log_data - log_data.mean(axis=0)) / log_data.std(axis=0)
        
        dist_matrix = euclidean_distances(scaled_data)
        
        k_range = range(2, 9)
        wcss_scores = []
        sil_scores = []
        
        for k in k_range:
            model = ManualKMeans(n_clusters=k, init='k-means++', random_state=42)
            model.fit(scaled_data)
            
            wcss_scores.append(model.inertia_)
            sil_scores.append(calculate_silhouette(scaled_data, model.labels, dist_matrix))
            
        # İş Kuralı: E-ticaret segmentasyonunda K=2 pazarlama açısından anlamsızdır.
        # Bu nedenle K=2 hesaplamalara dahil edilse bile, karar mekanizmasında göz ardı edilir.
        valid_sil_scores = sil_scores[1:] # K=2'yi (ilk elemanı) atla
        valid_k_range = list(k_range)[1:] 
        
        best_k_idx = np.argmax(valid_sil_scores)
        best_k = valid_k_range[best_k_idx]
        
        project_params[dataset_name] = {
            "optimal_k": int(best_k)
        }
        
        print(f"K-Means++ ve Silhouette Optimizasyonu tamamlandı. Seçilen K: {best_k}")
        
        # Çift eksenli profesyonel raporlama grafiği
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        color1 = '#e74c3c'
        ax1.set_xlabel('Küme Sayısı (K)', fontweight='bold')
        ax1.set_ylabel('WCSS (Hata Kareler Toplamı)', color=color1, fontweight='bold')
        ax1.plot(k_range, wcss_scores, color=color1, marker='o', linewidth=2, label='WCSS (Elbow)')
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)

        ax2 = ax1.twinx()  
        color2 = '#2980b9'
        ax2.set_ylabel('Silhouette Skoru', color=color2, fontweight='bold')  
        ax2.plot(k_range, sil_scores, color=color2, marker='s', linewidth=2, label='Silhouette')
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # Seçilen K değerini işaretle
        ax2.axvline(x=best_k, color='#27ae60', linestyle='--', linewidth=2, label=f'Optimal K ({best_k})')
        
        plt.title(f"{dataset_name.upper()} Veri Seti - K-Değeri Optimizasyonu", fontweight='bold')
        
        # Legendları birleştir
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)
        
        fig.tight_layout()  
        plot_path = os.path.join(DOCS_DIR, f"eval_{dataset_name}.png")
        plt.savefig(plot_path)
        plt.close()
        
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(project_params, f, indent=4)
    print(f"\nBAŞARILI: Konfigürasyon dosyası kök dizine yazıldı ({CONFIG_PATH})")

if __name__ == "__main__":
    evaluate_models()