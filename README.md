
# E-Commerce Behavioral Clustering (RFM & K-Means)

Bu proje, e-ticaret veritabanları üzerinde RFM (Recency, Frequency, Monetary) analizi ve K-Means++ algoritmaları kullanarak davranışsal müşteri segmentasyonu gerçekleştiren veri işleme ve analiz hattıdır.

## 🏗️ Proje Mimarisi

Proje, modülerlik ve sürdürülebilirlik ilkelerine dayalı aşağıdaki dizin yapısı ile inşa edilmiştir:

```text
ecommerce-behavioral-clustering/
├── app/
│   └── dashboard.py          # Streamlit tabanlı interaktif yönetici paneli
├── data/
│   ├── raw/                  # Ham veri setleri (Git'e dahil edilmez)
│   └── processed/            # RFM analizinden geçmiş ara çıktılar
├── outputs/
│   ├── actions/              # Nihai pazarlama aksiyon planları ve müşteri listeleri
│   └── figures/              # K-Değeri optimizasyon grafikleri ve görsel çıktılar
├── docs/                     # Akademik raporlar ve proje sunumları
├── src/
│   ├── preprocessing.py      # Veri temizleme ve RFM metrik hesaplama motoru
│   ├── evaluation.py         # K-Means++ ve Silhouette Skoru optimizasyonu
│   ├── clustering.py         # Kümeleme işlemleri ve dinamik kupon üretimi
│   └── custom_algorithms.py  # Dışa bağımlılığı azaltan özel algoritma sınıfları
├── parameters.json           # Model konfigürasyonları ve optimal hiperparametreler
├── .gitignore                # Versiyon kontrol kısıtlamaları
├── requirements.txt          # Proje bağımlılıkları
└── README.md

```

## 📁 Proje Dokümantasyonu

Projenin teorik altyapısı, analiz sonuçları ve sunum dosyalarına aşağıdaki bağlantılardan ulaşabilirsiniz:

* [Proje Önerisi ve Literatür Taraması](https://www.google.com/search?q=docs/project-proposal.pdf) - Projenin kapsamı ve akademik arka planı.
* [Nihai Proje Raporu](https://www.google.com/search?q=docs/final-report.pdf) - Metodoloji, model bulguları ve sonuç analizi.
* [Proje Sunumu](https://www.google.com/search?q=docs/project-presentation.pdf) - Sürecin görsel ve yönetsel özeti.

## 👥 Geliştirici Ekibi

Bu proje aşağıdaki mühendisler tarafından tasarlanmış ve geliştirilmiştir:

* **Yücel Berk ÜNALDI** - [GitHub](https://github.com/yberkunaldi) 
* **Ali Bahadır UYUMAZ** - [GitHub](https://github.com/alibahadiruyumaz) | [LinkedIn](https://www.linkedin.com/in/ali-bahadir-uyumaz)
