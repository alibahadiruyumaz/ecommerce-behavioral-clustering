# E-Commerce Behavioral Clustering (RFM & K-Means)

Bu proje, e-ticaret veritabanları üzerinde RFM (Recency, Frequency, Monetary) analizi ve makine öğrenmesi (K-Means++) algoritmaları kullanarak davranışsal müşteri segmentasyonu gerçekleştiren uçtan uca bir veri boru hattıdır (data pipeline).

## 🏗️ Proje Mimarisi

Proje, spagetti kod yaklaşımından uzaklaştırılarak modüler, ölçeklenebilir ve yönetilebilir bir dizin hiyerarşisiyle inşa edilmiştir:

```text
ecommerce-behavioral-clustering/
├── app/
│   └── dashboard.py          # Streamlit tabanlı interaktif yönetici paneli
├── data/
│   ├── raw/                  # Ham veri setleri (Git'e dahil edilmez)
│   ├── processed/            # RFM analizinden geçmiş ara çıktılar
│   └── Final_Action_Plan_... # Pazarlama aksiyon planları ve listeler
├── docs/                     # K-Değeri optimizasyon grafikleri
├── src/
│   ├── preprocessing.py      # Veri temizleme ve RFM metrik hesaplama motoru
│   ├── evaluation.py         # K-Means++ ve Silhouette Skoru optimizasyonu
│   ├── clustering_and_action.py # Final kümeleme ve dinamik kupon üretimi
│   └── my_lib.py             # Dışa bağımlılığı azaltan özel algoritma sınıfları
├── parameters.json           # Model konfigürasyonları ve optimal K değerleri
├── .gitignore                # Versiyon kontrol kısıtlamaları
├── requirements.txt          # Proje bağımlılıkları
└── README.md

## 📁 Proje Dokümantasyonu

Projenin teorik altyapısı, analiz sonuçları ve sunum dosyalarına aşağıdaki bağlantılardan ulaşabilirsiniz:

* [Proje Önerisi ve Literatür Taraması](docs/project-proposal.pdf) - Projenin kapsamı ve akademik arka planı.
* [Nihai Proje Raporu](docs/final-report.pdf) - Metodoloji, bulgular ve sonuç analizi.
* [Proje Sunumu](docs/project-presentation.pdf) - Sürecin görsel özeti.