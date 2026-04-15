import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Admin Dashboard UMKM", layout="wide")

# ======================
# STYLE
# ======================
st.markdown("""
<style>

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1e293b;
}
[data-testid="stSidebar"] * {
    color: white;
}

/* Card */
.card {
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}
.card-blue { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }
.card-green { background: linear-gradient(135deg, #22c55e, #15803d); }
.card-orange { background: linear-gradient(135deg, #f59e0b, #b45309); }

.card h3 { margin: 0; font-size: 16px; }
.card h1 { margin: 5px 0 0 0; font-size: 28px; }

</style>
""", unsafe_allow_html=True)

# ======================
# LOAD DATA
# ======================
data = pd.read_csv('data_clean.csv')
rules = pd.read_csv('rules_per_toko.csv')

data['Tanggal'] = pd.to_datetime(data['Tanggal'])

# ======================
# SIDEBAR
# ======================
st.sidebar.title("📊 ADMIN PANEL")
menu = st.sidebar.radio("Menu", ["📋 Data UMKM", "📊 Dashboard"])

# ======================
# HALAMAN 1
# ======================
if menu == "📋 Data UMKM":

    st.title("📋 Data UMKM FNB Kota Pagar Alam")

    toko_list = sorted(data['Toko'].unique())

    for toko in toko_list:

        df_toko = data[data['Toko'] == toko]
        alamat = df_toko['Alamat'].iloc[0]

        with st.expander(f"🏪 {toko}"):

            st.write(f"📍 **Alamat:** {alamat}")

            produk = sorted(df_toko['Nama Produk'].unique())

            for p in produk:
                st.write(f"- {p}")

# ======================
# HALAMAN 2
# ======================
elif menu == "📊 Dashboard":

    st.title("📊 Dashboard UMKM Food & Beverage")

    # FILTER
    col1, col2 = st.columns(2)
    bulan = col1.selectbox("Pilih Bulan", sorted(data['Bulan'].unique()))
    tahun = col2.selectbox("Pilih Tahun", sorted(data['Tahun'].unique()))

    df = data[(data['Bulan'] == bulan) & (data['Tahun'] == tahun)]

    if df.empty:
        st.warning("Data tidak tersedia")
    else:

        # ======================
        # 🔝 CARD GLOBAL
        # ======================
        

        st.markdown("---")

        # ======================
        # PER TOKO
        # ======================
        toko_list = df['Toko'].unique()

        for toko in toko_list:

            st.markdown(f"## 🏪 {toko}")

            df_toko = df[df['Toko'] == toko]

            # ======================
            # CARD TOKO
            # ======================
            col1, col2, col3 = st.columns(3)

            total_transaksi_toko = df_toko.groupby(['Tanggal']).ngroups
            total_item_toko = df_toko['Terjual'].sum()

            produk_terlaris_toko = df_toko.groupby('Nama Produk')['Terjual'].sum().idxmax()

            with col1:
                st.markdown(f"""
                <div class="card card-blue">
                    <h3>Total Transaksi</h3>
                    <h1>{total_transaksi_toko}</h1>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="card card-green">
                    <h3>Produk Terlaris</h3>
                    <h1>{produk_terlaris_toko}</h1>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="card card-orange">
                    <h3>Total Item Terjual</h3>
                    <h1>{total_item_toko}</h1>
                </div>
                """, unsafe_allow_html=True)

            # ======================
            # GRAFIK
            # ======================
            st.markdown("### 📊 Grafik Produk Terlaris")

            top_produk = df_toko.groupby('Nama Produk')['Terjual'].sum().reset_index()
            top_produk = top_produk.sort_values(by='Terjual', ascending=False).head(10)

            fig = px.bar(top_produk, x='Nama Produk', y='Terjual', color='Terjual')
            st.plotly_chart(fig, use_container_width=True)

            # ======================
            # TABEL
            # ======================
            st.markdown("### 📋 Tabel Produk")

            st.dataframe(top_produk)

            # ======================
            # 🔥 APRIORI PER TOKO (FIX)
            # ======================
            st.markdown("### 🔗 Pola Pembelian")

            rules_toko = rules[rules['Toko'] == toko]

            if not rules_toko.empty:
                st.dataframe(rules_toko[['antecedents','consequents','support','confidence','lift']].head(5))

                for i, row in rules_toko.head(3).iterrows():
                    st.success(f"Jika membeli {row['antecedents']} → {row['consequents']}")
            else:
                st.info("Tidak ada pola ditemukan")

            st.markdown("---")