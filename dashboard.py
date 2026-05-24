
#dashboard.py
import streamlit as st
import pandas as pd
import json
import time
import altair as alt
import os


#n8n'deki Workflow ID
N8N_WORKFLOW_ID = "YOUR_N8N_WORKFLOW_ID_HERE" 
N8N_BASE_URL = "http://localhost:5678"

st.set_page_config(
    page_title="LogWeaver SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS ---
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 26px;
        color: #00FF41; /* Hacker Yeşili */
    }
    .stHeader {
        background-color: transparent;
    }
    thead tr th {
        font-weight: bold !important;
        color: #00FF41 !important;
    }
    /* Linklerin rengini düzelt */
    a {
        color: #00FF41 !important;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# VERİ OKUMA
def load_data():
    data_file = "dashboard_data.json"
    if not os.path.exists(data_file):
        return pd.DataFrame()

    data = []
    try:
        with open(data_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    line = line.strip()
                    if line:
                        json_obj = json.loads(line)
                        if "error" in json_obj: continue
                        data.append(json_obj)
                except json.JSONDecodeError:
                    continue
    except Exception:
        return pd.DataFrame()
    
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    
    # EKSİK VERİ TAMAMLAMA
    if "classification" not in df.columns: 
        df["classification"] = df.get("tespit", "Analiz Ediliyor...")
    if "source_ip" not in df.columns: 
        df["source_ip"] = "-"
    if "explanation" not in df.columns: 
        df["explanation"] = df.get("aciklama", "Açıklama yok.")
    if "saved_at" in df.columns:
        df["saved_at"] = pd.to_datetime(df["saved_at"], errors='coerce')

    # PRIORITY
    if "priority" in df.columns:
        df["priority"] = pd.to_numeric(df["priority"], errors='coerce').fillna(3).astype(int)
    else:
        df["priority"] = 3

    # AKSİYON VE LİNK MANTIĞI 
    def get_action_display(row):
        text = str(row.get("classification", "")).lower() + str(row.get("tespit", "")).lower()
        if "true positive" in text:
            return "⛔ IP Blocked (n8n)"
        else:
            return "✅ False Positive"

    def get_action_link(row):
        text = str(row.get("classification", "")).lower() + str(row.get("tespit", "")).lower()
        
        # SADECE True Positive ise Workflow Geçmişine Link Ver
        if "true positive" in text:
            # Direkt o workflow'un executions sayfasına gider
            return f"{N8N_BASE_URL}/workflow/{N8N_WORKFLOW_ID}/executions"
        else:
            return None

    df["action_display"] = df.apply(get_action_display, axis=1)
    df["action_link"] = df.apply(get_action_link, axis=1)
    
    return df

# YÜKLEME 
df = load_data()

# SIDEBAR 
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=60)
    st.title("LogWeaver")
    st.caption("AI-Driven Threat Intelligence")
    st.divider()

    st.subheader("⚡ SOAR Durumu")
    st.success("n8n Servisi: Aktif")
    # Butonu da güncelledik: Direkt Executions'a gider
    st.link_button("SOAR Geçmişini Görüntüle", f"{N8N_BASE_URL}/workflow/{N8N_WORKFLOW_ID}/executions", use_container_width=True)
    st.divider()

    # Filtreler
    if not df.empty:
        unique_p = sorted(df["priority"].unique())
        labels = {1: "1 - Kritik", 2: "2 - Orta", 3: "3 - Bilgi"}
        sel_p = st.multiselect("Öncelik Filtresi", unique_p, format_func=lambda x: labels.get(x, str(x)), default=unique_p)
        if sel_p:
            df_filtered = df[df["priority"].isin(sel_p)]
        else:
            df_filtered = df
    else:
        df_filtered = df
    
    st.caption(f"Log Sayısı: {len(df_filtered)}")

# ANA EKRAN 
if df_filtered.empty:
    st.warning(" Bekleniyor... Veri akışı yok.")
else:
    # KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🛡️ Toplam Analiz", len(df))
    
    if "source_ip" in df_filtered.columns:
        valid = df_filtered[df_filtered["source_ip"] != "-"]
        if not valid.empty:
            att = valid["source_ip"].value_counts().idxmax()
            cnt = valid["source_ip"].value_counts().max()
            k2.metric(" En Çok Saldıran", att, f"{cnt} Kez")
        else:
            k2.metric(" En Çok Saldıran", "-", "0")
            
    # True Positive Sayısı
    tp_count = len(df_filtered[df_filtered["classification"].astype(str).str.contains("True Positive", case=False, na=False)])
    k3.metric("Gerçek Tehditler", tp_count)
    
    if "saved_at" in df_filtered.columns and not df_filtered["saved_at"].isnull().all():
        last = df_filtered["saved_at"].max().strftime("%H:%M:%S")
        k4.metric("Son Olay", last, "Canlı")

    st.markdown("---")

    # GRAFİKLER
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Saldırı Trafiği (Siber Nabız)")
        if "saved_at" in df_filtered.columns:
            valid_d = df_filtered[df_filtered["saved_at"].notnull()]
            
            if not valid_d.empty:
               
                # Veriyi 10 saniyelik dilimlere bölüp sayıyoruz. 
                # Böylece 1-1-1 yerine 3-5-2 gibi dalgalanma oluşur.
                chart_data = valid_d.set_index('saved_at').resample('10s').size().reset_index(name='count')
                
                # Eğer veri çok azsa boşlukları 0 ile doldur ki grafik kopmasın
                # (İsteğe bağlı, akışkanlık için)
                
                # GRAFİK TASARIMI 
                chart = alt.Chart(chart_data).mark_area(
                    line={'color':'#00FF41', 'size': 4}, 
                    color=alt.Gradient(
                        gradient='linear',
                        stops=[alt.GradientStop(color='rgba(0, 255, 65, 0.6)', offset=0),  
                               alt.GradientStop(color='rgba(0, 255, 65, 0.05)', offset=1)], 
                        x1=1, x2=1, y1=1, y2=0
                    ),
                    interpolate='monotone' 
                ).encode(
                    x=alt.X('saved_at:T', 
                            title=None,
                            axis=alt.Axis(format='%H:%M:%S', grid=True, gridOpacity=0.1, tickCount=5)),
                    y=alt.Y('count:Q', 
                            title='Yoğunluk',
                            axis=alt.Axis(tickMinStep=1)), # Ondalıklı sayı göstermesin (1.5 saldırı olmaz)
                    tooltip=[
                        alt.Tooltip('saved_at', title='Zaman Aralığı', format='%H:%M:%S'),
                        alt.Tooltip('count', title='Tespit Sayısı')
                    ]
                ).properties(
                    height=250
                ).configure_view(
                    strokeWidth=0 
                )
                
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Grafik için veri bekleniyor...")
    with c2:
        st.subheader(" True vs False Positive")
        if "classification" in df_filtered.columns:
            donut = alt.Chart(df_filtered).mark_arc(innerRadius=50).encode(
                theta=alt.Theta("count()", stack=True),
                color=alt.Color("classification", legend=None),
                tooltip=["classification", "count()"]
            ).properties(height=250)
            st.altair_chart(donut, use_container_width=True)

    # TABLO 
    st.subheader(" Güvenlik Olayları ve Aksiyon Durumu")
    
    display_cols = ["saved_at", "priority", "classification", "source_ip", "action_display", "action_link"]
    final_cols = [c for c in display_cols if c in df_filtered.columns]
    
    df_show = df_filtered[final_cols].sort_index(ascending=False)

    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "saved_at": st.column_config.DatetimeColumn("Zaman", format="HH:mm:ss", width="small"),
            "priority": st.column_config.NumberColumn("Önem", format="%d", width="small"),
            "classification": st.column_config.TextColumn("Tespit Türü", width="medium"),
            "source_ip": st.column_config.TextColumn("Kaynak IP", width="medium"),
            "action_display": st.column_config.TextColumn("SOC Durumu", width="medium"),
            "action_link": st.column_config.LinkColumn(
                "Müdahale Linki",
                display_text=" n8n Workflow History", 
                help="Olayın n8n üzerindeki işlem geçmişini gör.",
                width="medium"
            )
        }
    )

    # DETAY KUTUSU
    if not df_show.empty:
        last_event = df_filtered.sort_index(ascending=False).iloc[0]
        text_chk = str(last_event.get('classification', '')).lower() + str(last_event.get('tespit', '')).lower()
        is_tp = "true positive" in text_chk

        with st.expander(" SON OLAY DETAYI", expanded=True):
            col_d1, col_d2 = st.columns([1, 3])
            with col_d1:
                st.markdown(f"**IP:** `{last_event.get('source_ip')}`")
                if is_tp:
                    st.error("DURUM: ENGELLENDİ")
                else:
                    st.success("DURUM: FALSE POSITIVE")
            
            with col_d2:
                st.markdown("**Açıklama:**")
                st.caption(last_event.get('explanation', '...'))
                if is_tp:
                    st.error(" AKSİYON: Bu IP adresi gerçek bir tehdit olarak belirlendi ve n8n üzerinden engellendi.")
                else:
                    st.success(" AKSİYON: Tehdit skoru düşük veya yanlış alarm. İşlem yapılmadı.")

time.sleep(3)
st.rerun()