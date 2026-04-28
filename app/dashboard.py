import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="E-ticaret Davranışsal Segmentasyon Paneli",
    page_icon="🎯",
    layout="wide"
)

# Temel stil tanımlamaları
st.markdown("""
<style>
    .metric-card {background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 5px solid #2ecc71; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px;}
    h1, h2, h3 {color: #2c3e50;}
</style>
""", unsafe_allow_html=True)

# Dizin mimarisini projeye uygun hale getir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data")
DOCS_DIR = os.path.join(BASE_DIR, "../docs")

# Final rapor dosyalarını bul
available_projects = [
    f.replace("Final_Action_Plan_", "").replace(".xlsx", "") 
    for f in os.listdir(DATA_DIR) 
    if f.startswith("Final_Action_Plan_") and f.endswith(".xlsx")
]

if not available_projects:
    st.error("🚨 HATA: data/ klasöründe Final_Action_Plan_...xlsx dosyaları bulunamadı. Lütfen önce veri boru hattını (pipeline) çalıştırın.")
    st.stop()

# Ortak renk paleti (Segmentler için)
color_map = {
    "Champions": "#2ecc71",
    "Loyal Customers": "#3498db",
    "Potential Loyalists": "#f1c40f",
    "At Risk": "#e67e22",
    "Hibernating": "#e74c3c"
}

with st.sidebar:
    st.title("Proje Yönetimi")
    selected_project = st.selectbox("📂 Aktif Veri Seti:", available_projects)
    st.info(f"**{selected_project.upper()}**")
    st.write("---")

st.title(f"📊 360° Müşteri Analizi: {selected_project.upper()}")

tab1, tab2, tab3 = st.tabs(["🔬 1. Algoritma Performansı", "💎 2. Segment Profilleri", "🚀 3. Aksiyon Merkezi"])

with tab1:
    st.subheader("🔍 K-Değeri Optimizasyon Kanıtları")
    
    eval_path = os.path.join(DOCS_DIR, f"eval_{selected_project}.png")
    if os.path.exists(eval_path):
        st.image(eval_path, caption="Çift Eksenli (Elbow & Silhouette) Analiz", use_container_width=True)
    else:
        st.warning("Değerlendirme (Evaluation) grafiği docs klasöründe bulunamadı.")
        
    st.markdown("""
    **Analitik Yaklaşım:** Müşterileri sadece ikiye bölmek e-ticaret dinamiklerine aykırı olduğundan, 
    K=2 seçeneği bir iş kuralı (business rule) olarak yasaklanmış ve en yüksek Silhouette skorunu veren 
    diğer optimal K değeri tercih edilmiştir.
    """)

with tab2:
    file_path = os.path.join(DATA_DIR, f"Final_Action_Plan_{selected_project}.xlsx")
    try:
        df = pd.read_excel(file_path, sheet_name="Customer_List")
        
        # Temel Metrikler
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👥 Toplam Müşteri", f"{len(df):,}")
        k2.metric("💰 Toplam Ciro", f"{df['Monetary'].sum():,.0f} TL")
        k3.metric("🛒 Ortalama Sepet", f"{df['Monetary'].mean():,.0f} TL")
        k4.metric("📊 K-Değeri (Küme Sayısı)", f"{df['Segment'].nunique()}")
        
        st.markdown("---")
        
        col_3d, col_bar = st.columns([1.5, 1])
        
        with col_3d:
            st.subheader("🧊 3D Segment Dağılımı")
            fig_3d = px.scatter_3d(
                df, x='Recency', y='Frequency', z='Monetary',
                color='Segment', opacity=0.7, size_max=10,
                hover_data=['Coupon_Code'],
                color_discrete_map=color_map,
            )
            fig_3d.update_layout(
                margin=dict(l=0, r=0, b=0, t=0),
                scene=dict(aspectmode='cube'),
                legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center", title=None)
            )
            st.plotly_chart(fig_3d, use_container_width=True)
            
        with col_bar:
            st.subheader("📋 Segment Karnesi")
            summary_df = pd.read_excel(file_path, sheet_name="Executive_Summary")
            st.dataframe(
                summary_df,
                column_config={
                    "Recency": st.column_config.NumberColumn("Ort. Gün", format="%.1f"),
                    "Frequency": st.column_config.NumberColumn("Ort. Sipariş", format="%.1f"),
                    "Monetary": st.column_config.NumberColumn("Ort. Harcama", format="%.0f ₺"),
                    "Customer_Count": st.column_config.NumberColumn("Kişi Sayısı", format="%d")
                },
                use_container_width=True,
                hide_index=False
            )

    except Exception as e:
        st.error(f"Veri okuma hatası: {e}")

with tab3:
    st.header("🎯 Aksiyon Simülasyonu")
    
    if 'df' in locals():
        target_seg = st.selectbox("Hedef Kitle Seçimi:", df["Segment"].unique())
        seg_data = df[df["Segment"] == target_seg]
        
        if not seg_data.empty:
            sample = seg_data.sample(1).iloc[0]
            discount_display = f"%{int(sample['Discount_Rate'] * 100)}"
            
            c1, c2 = st.columns([2, 1])
            with c1:
                st.info("📢 **Örnek Kampanya İçeriği**")
                st.code(sample['Message'], language="text")
                st.write(f"🏷️ **Örnek Kod:** `{sample['Coupon_Code']}` | **İndirim Oranı:** **{discount_display}**")
            
            with c2:
                st.success("🚀 **Durum Paneli**")
                st.metric("Bu Kampanyanın Gideceği Kişi Sayısı", f"{len(seg_data)}")
                if st.button("Kampanyayı Başlat", type="primary"):
                    st.toast(f"✅ {target_seg} segmenti için kampanya tetiklendi!", icon="🔥")
            
            st.write("📋 **Hedef Müşteri Listesi (İlk 20)**")
            display_cols = [c for c in ["CustomerID", "Customer ID", "Recency", "Frequency", "Monetary", "Coupon_Code"] if c in seg_data.columns]
            st.dataframe(seg_data[display_cols].head(20), use_container_width=True)