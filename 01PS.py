import streamlit as st
import sqlite3 as sql
import pandas as pd

st.title("PERSONNAL-SON")

left_menu=st.sidebar.selectbox(
    "MENÜ",
    ["Giriş","Ekle", "Güncelleme", "Silme", "Sorgulama", "Listeleme"]
)
if left_menu == "Giriş":
    st.header("Teşekkürler")
    st.text("Bu proje Arı Bilgi Eğitim Kurumu'ndan aldığım python eğitiminin sonunda elde edeceğim "
            "Python Yazılım Uzmanlığı Sertifikasını almaya hak kazandıran proje olacaktır. Tüm Arı Bilgi"
            " yetkililerine ve de özellikle bizde emeği geçen Sayın Sinan Dilavere saygılarımı sunmaktayım. ")
elif left_menu == "Ekle":
    st.header("KİŞİ EKLE")
    with st.form("Ekle"):
        id=st.text_input("ID")
        ad=st.text_input("Adı")
        sa=st.text_input("Soyadı")
        dy=st.text_input("Doğum yeri")
        dt=st.text_input("Doğum tarihi")
        dp = st.text_input("Departmanı")
        gorevi=st.text_input("Görevi")
        ok=st.form_submit_button("Ekle")
    if ok:
        conn = sql.connect("AriBVeriT.db")
        verit = conn.cursor()
        sql_command="""INSERT INTO PERSONEL(ID, ADI, SOYADI, DOGUMYERI, DOGUMTARIHI, DEPARTMANI, GOREVI)
        VALUES(?,?,?,?,?,?,?)"""
        verit.execute(sql_command,[id,ad,sa,dy,dt,dp,gorevi])
        st.success("Kişi başarıyla eklendi.")
        conn.commit()
        conn.close()

elif left_menu == "Güncelleme":
    st.header("GÜNCELLEME")

    conn = sql.connect("AriBVeriT.db")
    verit = conn.cursor()

    df = pd.read_sql("SELECT * FROM PERSONEL", conn)

    if df.empty:
        st.warning("Güncellenecek veri bulunamadı.")
    else:
        secili_id = st.selectbox("Güncellemek istediğiniz kişinin ID'si:", df["ID"])
        secili_kisi = df[df["ID"] == secili_id].iloc[0]

        with st.form("Güncelleme"):
            ad = st.text_input("Ad", secili_kisi["ADI"])
            sa = st.text_input("Soyad", secili_kisi["SOYADI"])
            dy = st.text_input("Doğum Yeri", secili_kisi["DOGUMYERI"])
            dt = st.text_input("Doğum Tarihi", secili_kisi["DOGUMTARIHI"])
            dp = st.text_input("Departman", secili_kisi["DEPARTMANI"])
            gorevi = st.text_input("Görevi", secili_kisi["GOREVI"])

            guncelle = st.form_submit_button("Güncelle")
            if guncelle:
                sql_command = """
                    UPDATE PERSONEL
                    SET ADI=?, SOYADI=?, DOGUMYERI=?, DOGUMTARIHI=?, DEPARTMANI=?, GOREVI=? 
                    WHERE ID=?
                """
                verit.execute(sql_command, [ad, sa, dy, dt, dp, gorevi, secili_id])
                conn.commit()
                st.success("Kayıt başarıyla güncellendi.")

    conn.close()

elif left_menu == "Silme":
    st.header("Personel Silme")

    if st.session_state.get("silindi", False):
        st.success("Kayıtlar başarıyla silindi.")
        st.session_state["silindi"] = False

    conn = sql.connect("AriBVeriT.db")
    df = pd.read_sql("SELECT * FROM PERSONEL", conn)

    if df.empty:
        st.warning("Silinecek kayıt bulunamadı.")
    else:
        st.subheader("Mevcut Personel Listesi")
        st.dataframe(df, use_container_width=True)

        secenekler = df.apply(lambda row: f"{row['ID']} - {row['ADI']} {row['SOYADI']}", axis=1).tolist()
        secimler = st.multiselect("Silmek istediğiniz kişileri seçin:", secenekler)

        if st.button("Seçilenleri Sil"):
            if not secimler:
                st.warning("Lütfen en az bir kişi seçin.")
            else:
                secilen_idler = [int(s.split(" - ")[0]) for s in secimler]
                cursor = conn.cursor()
                cursor.executemany("DELETE FROM PERSONEL WHERE ID = ?", [(i,) for i in secilen_idler])
                conn.commit()
                conn.close()

                st.session_state["silindi"] = True  # Başarı mesajı için işaretle
                st.rerun()  # Sayfayı yenile

    conn.close()
elif left_menu == "Sorgulama":
    st.header("Personel Sorgulama")

    conn = sql.connect("AriBVeriT.db")
    df = pd.read_sql("SELECT * FROM PERSONEL", conn)

    if df.empty:
        st.warning("Veritabanında kayıt yok.")
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["ID'ye Göre", "Ada Göre", "Soyada göre", "Departmana Göre"])

        with tab1:
            st.subheader("ID ile Sorgulama")
            sec_id = st.text_input("ID girin:")
            if st.button("Sorgula", key="id_sorgula"):
                if sec_id.strip() == "":
                    st.warning("Lütfen bir ID girin.")
                else:
                    result = df[df["ID"].astype(str) == sec_id.strip()]
                    if result.empty:
                        st.error("Bu ID ile eşleşen kayıt bulunamadı.")
                    else:
                        st.dataframe(result, use_container_width=True)

        with tab2:
            st.subheader("Ada göre Sorgulama")
            sec_ad = st.text_input("Ad girin:")
            if st.button("Sorgula", key="ad_sorgula"):
                if sec_ad.strip() == "":
                    st.warning("Lütfen bir isim girin.")
                else:
                    result = df[
                        df["ADI"].str.contains(sec_ad, case=False)
                        ]
                    if result.empty:
                        st.error("Bu isimle eşleşen kayıt bulunamadı.")
                    else:
                        st.dataframe(result, use_container_width=True)
        with tab3:
            st.subheader("Soyada göre Sorgulama")
            sec_soy = st.text_input("Soyad girin:")
            if st.button("Sorgula", key="soy_sorgula"):
                if sec_soy.strip() == "":
                    st.warning("Soyad girin.")
                else:
                    result = df[
                        df["SOYADI"].str.contains(sec_soy, case=False)
                        ]
                    if result.empty:
                        st.error("Bu isimle eşleşen kayıt bulunamadı.")
                    else:
                        st.dataframe(result, use_container_width=True)

        with tab4:
            st.subheader("Departmana Göre Sorgulama")
            unique_departmanlar = df["DEPARTMANI"].unique()
            secilen_departman = st.selectbox("Departman seçin:", unique_departmanlar)
            if st.button("Sorgula", key="dp_sorgula"):
                result = df[df["DEPARTMANI"] == secilen_departman]
                st.dataframe(result, use_container_width=True)

    conn.close()

elif left_menu == "Listeleme":
    st.header("Personel Listeleme")

    conn = sql.connect("AriBVeriT.db")
    df = pd.read_sql("SELECT * FROM PERSONEL", conn)

    if df.empty:
        st.warning("Veritabanında kayıt bulunamadı.")
    else:
        st.dataframe(df, use_container_width=True)

    conn.close()
