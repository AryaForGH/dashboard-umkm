import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Dashboard UMKM", layout="wide")

# ======================
# SESSION STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_toko" not in st.session_state:
    st.session_state.selected_toko = None

# ======================
# STYLE (CLEAN MODERN)
# ======================
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

/* TITLE */
h1, h2, h3 {
    color: #f1f5f9;
}

/* CARD CLEAN */
.card-clean {
    background: #1e293b;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: 0.2s;
    margin-bottom: 8px;
}

.card-clean:hover {
    transform: translateY(-3px);
    background: #273449;
}

/* TITLE CARD */
.card-title {
    font-size: 16px;
    font-weight: 600;
    color: #f1f5f9;
}

/* SUBTEXT */
.card-sub {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 5px;
}

/* CARD DASHBOARD */
.card {
    padding: 20px;
    border-radius: 14px;
    background: #1e293b;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
}

/* BUTTON */
.stButton>button {
    border-radius: 10px;
    height: 35px;
    font-size: 13px;
    background: #3b82f6;
    border: none;
    transition: 0.2s;
    color: white;
}

.stButton>button:hover {
    background: #2563eb;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 10px;
}

/* SPACING */
.block-container {
    padding-top: 2rem;
}

</style>u
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
data = pd.read_csv('data_clean.csv')
rules = pd.read_csv('rules_per_toko_baru.csv')

data['Tanggal'] = pd.to_datetime(data['Tanggal'])

# ======================
# HOME (LIST TOKO)
# ======================
if st.session_state.page == "home":

    st.markdown("""
    <h1>🏪 UMKM F&B Pagar Alam</h1>
    <p style='color:#94a3b8;'>Pilih toko untuk melihat detail dan analisis</p>
    """, unsafe_allow_html=True)

    # SEARCH
    search = st.text_input("🔍 Cari Toko")

    toko_list = sorted(data['Toko'].unique())

    if search:
        toko_list = [t for t in toko_list if search.lower() in t.lower()]

    cols = st.columns(4)

    for i, toko in enumerate(toko_list):
        with cols[i % 4]:

            st.markdown(f"""
            <div class="card-clean">
                <div class="card-title">🏪 {toko}</div>
                <div class="card-sub">Klik untuk melihat detail</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Lihat Detail", key=f"btn_{toko}", use_container_width=True):
                st.session_state.selected_toko = toko
                st.session_state.page = "detail"
                st.rerun()

# ======================
# DETAIL TOKO
# ======================
elif st.session_state.page == "detail":

    toko = st.session_state.selected_toko
    df_toko = data[data['Toko'] == toko]

    st.markdown(f"<h1>🏪 {toko}</h1>", unsafe_allow_html=True)

    alamat = df_toko['Alamat'].iloc[0]

    # ALAMAT
    st.markdown(f"""
    <div class="card">
        <h3>📍 Alamat</h3>
        <p>{alamat}</p>
    </div>
    """, unsafe_allow_html=True)

    # MENU
    st.markdown("### 🍽️ Daftar Menu")

    produk = sorted(df_toko['Nama Produk'].unique())

    cols = st.columns(4)
    for i, p in enumerate(produk):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="card-clean">{p}</div>
            """, unsafe_allow_html=True)

    st.markdown("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ Kembali"):
            st.session_state.page = "home"
            st.rerun()

    with col2:
        if st.button("📊 Lihat Analisis"):
            st.session_state.page = "analisis"
            st.rerun()

# ======================
# ANALISIS
# ======================
elif st.session_state.page == "analisis":

    toko = st.session_state.selected_toko
    df_all = data[data['Toko'] == toko]

    st.markdown(f"<h1>📊 Analisis {toko}</h1>", unsafe_allow_html=True)

    # FILTER
    col1, col2 = st.columns(2)
    bulan = col1.selectbox("Pilih Bulan", sorted(df_all['Bulan'].unique()))
    tahun = col2.selectbox("Pilih Tahun", sorted(df_all['Tahun'].unique()))

    df = df_all[(df_all['Bulan'] == bulan) & (df_all['Tahun'] == tahun)]

    if df.empty:
        st.warning("Data tidak tersedia")
    else:

        # CARD
        col1, col2, col3 = st.columns(3)

        total_transaksi = df.groupby(['Tanggal']).ngroups
        total_item = df['Terjual'].sum()
        produk_terlaris = df.groupby('Nama Produk')['Terjual'].sum().idxmax()

        with col1:
            st.markdown(f"""
            <div class="card">
                <h3>Total Transaksi</h3>
                <h1>{total_transaksi}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="card">
                <h3>Produk Terlaris</h3>
                <h1>{produk_terlaris}</h1>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="card">
                <h3>Total Item</h3>
                <h1>{total_item}</h1>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # GRAFIK
        st.markdown("### 📊 Grafik Penjualan")

        top_produk = df.groupby('Nama Produk')['Terjual'].sum().reset_index()
        top_produk = top_produk.sort_values(by='Terjual', ascending=False).head(10)

        fig = px.bar(top_produk, x='Nama Produk', y='Terjual', color='Terjual')
        st.plotly_chart(fig, use_container_width=True)

        # TABEL
        st.markdown("### 📋 Data Produk")
        st.dataframe(top_produk)

        # ======================
        # 🔗 POLA PEMBELIAN (UI IMPROVED)
        # ======================
        st.markdown("### 🔗 Pola Pembelian (Association Rules)")

        rules_toko = rules[rules['Toko'] == toko]

        if not rules_toko.empty:

            # format angka
            rules_toko = rules_toko.copy()
            rules_toko['support'] = rules_toko['support'].round(3)
            rules_toko['confidence'] = rules_toko['confidence'].round(3)
            rules_toko['lift'] = rules_toko['lift'].round(3)

            # ======================
            # TABEL
            # ======================
            with st.expander("📋 Lihat Tabel Lengkap"):
                st.dataframe(rules_toko[['antecedents','consequents','support','confidence','lift']])

            # ======================
            # INSIGHT CARD
            # ======================
            st.markdown("#### 💡 Insight Pola Pembelian")

            for i, row in rules_toko.head(5).iterrows():

                antecedent = row['antecedents']
                consequent = row['consequents']
                support = row['support']
                confidence = row['confidence']
                lift = row['lift']

                # klasifikasi hubungan
                if lift > 0.7:
                    hubungan = "🟢 Kuat"
                elif lift >= 0.6:
                    hubungan = "🟡 Netral"
                else:
                    hubungan = "🔴 Lemah"

                # CARD UTAMA
                st.markdown(f"""
                <div style="
                    background:#1e293b;
                    padding:20px;
                    border-radius:12px;
                    margin-bottom:15px;
                    border:1px solid rgba(255,255,255,0.05)
                ">
                    <h4 style="margin-bottom:10px;">📌 {antecedent} ➜ {consequent}</h4>
                    <p style="color:#94a3b8; font-size:13px;">
                    Jika pelanggan membeli <b>{antecedent}</b>, maka cenderung membeli <b>{consequent}</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # METRIC (3 KOLOM)
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Support", f"{support}", f"{round(support*100,1)}%")

                with col2:
                    st.metric("Confidence", f"{confidence}", f"{round(confidence*100,1)}%")

                with col3:
                    st.metric("Lift", f"{lift}", hubungan)

                # INTERPRETASI
                st.markdown(f"""
                <div style="
                    background:#0f172a;
                    padding:15px;
                    border-radius:10px;
                    margin-top:10px;
                    margin-bottom:25px;
                    color:#cbd5f5;
                    font-size:14px;
                ">
                🧠 <b>Interpretasi:</b><br>
                Pelanggan yang membeli <b>{antecedent}</b> memiliki kemungkinan sebesar 
                <b>{round(confidence*100,1)}%</b> untuk juga membeli <b>{consequent}</b>.<br>
                Nilai lift <b>{lift}</b> menunjukkan hubungan <b>{hubungan}</b>.
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("Tidak ada pola pembelian yang ditemukan")

    if st.button("⬅️ Kembali"):
        st.session_state.page = "detail"
        st.rerun()
