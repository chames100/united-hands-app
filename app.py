# app.py - United Hands (version complète)
# Dépendances : streamlit, pandas, sqlalchemy
# pip install streamlit pandas sqlalchemy

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import hashlib
import os

# ----------------- Configuration -----------------
DB_PATH = "sqlite:///data.db"
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})

st.set_page_config(
    page_title="United Hands - Plateforme",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- Helpers DB -----------------
def init_db():
    """Initialise toutes les tables nécessaires."""
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS job_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            requirements TEXT,
            contact TEXT,
            published_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS housing_ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            city TEXT,
            address TEXT,
            price TEXT,
            description TEXT,
            contact TEXT,
            published_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            provider TEXT,
            start_date TEXT,
            duration TEXT,
            description TEXT,
            contact TEXT,
            published_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT,
            amount REAL,
            method TEXT,
            note TEXT,
            donated_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            created_at TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            timestamp TEXT
        );
        """))
    return

def insert(table: str, data: dict):
    """Insert dict into table with named params (SQLAlchemy text)."""
    if not data:
        return
    keys = ", ".join(data.keys())
    vals = ", ".join([f":{k}" for k in data.keys()])
    sql = text(f"INSERT INTO {table} ({keys}) VALUES ({vals})")
    with engine.begin() as conn:
        conn.execute(sql, **data)

def read_table(table: str) -> pd.DataFrame:
    """Return pandas DataFrame for table. If table missing, return empty df."""
    try:
        with engine.connect() as conn:
            df = pd.read_sql_table(table, conn)
        return df
    except Exception:
        return pd.DataFrame()

def format_datetime_now():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# ----------------- Utils utilisateur -----------------
def hash_pwd(p: str) -> str:
    return hashlib.sha256(p.encode()).hexdigest()

def ensure_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None

# ----------------- THEME (optionnel fichier .streamlit/config.toml) -----------------
# Pour appliquer le thème globalement, créez un fichier .streamlit/config.toml avec le contenu :
# [theme]
# primaryColor="#0D6EFD"
# backgroundColor="#F2F5F9"
# secondaryBackgroundColor="#FFFFFF"
# textColor="#1A1A1A"
# font="sans serif"

# ----------------- UI : Banner -----------------
def banner():
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #0D6EFD, #4BA3FF);
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin-bottom: 14px;
    ">
        <h1 style="margin:0; font-size:36px;">UNITED HANDS</h1>
        <p style="margin:4px 0 0 0; font-size:16px;">Unir les mains, ouvrir les horizons</p>
    </div>
    """, unsafe_allow_html=True)

# ----------------- Sidebar Navigation (menu moderne) -----------------
def sidebar_navigation():
    st.sidebar.markdown("<h3 style='text-align:center;'>📌 Menu</h3>", unsafe_allow_html=True)
    options = [
        "🏠 Accueil",
        "📤 Publier une annonce",
        "📋 Consulter les annonces",
        "💙 Faire un don",
        "📊 Tableau de bord",
        "👤 Profil",
        "💬 Chat",
        "🔐 Connexion / Inscription",
        "🔎 Statistiques (admin)"
    ]
    choice = st.sidebar.radio("", options)
    return choice

# ----------------- HOME (avec logo et slogan) -----------------
def home():
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    logo_path = "unitedhands_logo.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)
    else:
        st.markdown("<h3 style='color:#0D6EFD;'>UNITED HANDS</h3>", unsafe_allow_html=True)
    st.markdown("""
        <h2 style='text-align:center; color:#0D6EFD;'>Bienvenue sur United Hands</h2>
        <p style='text-align:center; font-size:16px; color:#333;'>
        La plateforme d'accompagnement pour les jeunes sortants des établissements de protection sociale.<br>
        Trouvez des offres d'emploi, des logements, des formations et bénéficiez d'un accompagnement.
        </p>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # boutons d'accès rapide
    st.write("")
    c1, c2, c3 = st.columns(3)
    if c1.button("🔎 Offres d'emploi"):
        st.session_state["_goto"] = "job"
    if c2.button("🏠 Logements"):
        st.session_state["_goto"] = "housing"
    if c3.button("📘 Formations"):
        st.session_state["_goto"] = "training"

    st.write("")
    st.markdown("<div style='text-align:center;color:gray'>Ensemble, nous construisons un avenir plus stable et solidaire.</div>", unsafe_allow_html=True)

# ----------------- Publish forms -----------------
def publish_form():
    st.header("Publier une nouvelle annonce")
    typ = st.selectbox("Type d'annonce", ["Offre d'emploi", "Logement", "Formation"])

    if typ == "Offre d'emploi":
        with st.form("job_form"):
            title = st.text_input("Titre du poste *")
            company = st.text_input("Entreprise")
            location = st.text_input("Localisation (ville/quartier)")
            description = st.text_area("Description")
            requirements = st.text_area("Exigences / Compétences requises")
            contact = st.text_input("Contact (email / téléphone)")
            submitted = st.form_submit_button("Publier l'offre")
            if submitted:
                if not title.strip():
                    st.error("Veuillez saisir un titre.")
                else:
                    insert("job_offers", {
                        "title": title.strip(),
                        "company": company.strip(),
                        "location": location.strip(),
                        "description": description.strip(),
                        "requirements": requirements.strip(),
                        "contact": contact.strip(),
                        "published_at": format_datetime_now()
                    })
                    st.success("Offre d'emploi publiée avec succès.")

    elif typ == "Logement":
        with st.form("housing_form"):
            title = st.text_input("Titre de l'annonce *")
            city = st.text_input("Ville")
            address = st.text_input("Adresse (optionnel)")
            price = st.text_input("Prix / Loyer (DH)")
            description = st.text_area("Description (taille, équipements, proximité...)")
            contact = st.text_input("Contact (email / téléphone)")
            submitted = st.form_submit_button("Publier l'annonce logement")
            if submitted:
                if not title.strip():
                    st.error("Veuillez saisir un titre.")
                else:
                    insert("housing_ads", {
                        "title": title.strip(),
                        "city": city.strip(),
                        "address": address.strip(),
                        "price": price.strip(),
                        "description": description.strip(),
                        "contact": contact.strip(),
                        "published_at": format_datetime_now()
                    })
                    st.success("Annonce logement publiée avec succès.")

    else:  # Formation
        with st.form("training_form"):
            title = st.text_input("Titre de la formation *")
            provider = st.text_input("Organisme / Fournisseur")
            start_date = st.date_input("Date de début (optionnel)")
            duration = st.text_input("Durée (ex: 2 semaines, 3 mois)")
            description = st.text_area("Description du contenu")
            contact = st.text_input("Contact (email / téléphone)")
            submitted = st.form_submit_button("Publier la formation")
            if submitted:
                if not title.strip():
                    st.error("Veuillez saisir un titre.")
                else:
                    insert("trainings", {
                        "title": title.strip(),
                        "provider": provider.strip(),
                        "start_date": start_date.strftime("%Y-%m-%d") if start_date else None,
                        "duration": duration.strip(),
                        "description": description.strip(),
                        "contact": contact.strip(),
                        "published_at": format_datetime_now()
                    })
                    st.success("Annonce formation publiée avec succès.")

# ----------------- View announcements -----------------
def view_announcements():
    st.header("Consulter les annonces")
    tabs = st.tabs(["Offres d'emploi", "Logement", "Formations"])
    with tabs[0]:
        df_jobs = read_table("job_offers")
        if df_jobs.empty:
            st.info("Aucune offre d'emploi pour le moment.")
        else:
            q = st.text_input("Rechercher (poste, entreprise, ville)...", key="job_search")
            df = df_jobs.copy()
            if q:
                mask = df.apply(lambda row: q.lower() in " ".join(map(str, row.values)).lower(), axis=1)
                df = df[mask]
            for _, row in df.sort_values("published_at", ascending=False).iterrows():
                st.subheader(f"{row['title']} — {row.get('company','')}")
                st.caption(f"Publié le : {row['published_at']}")
                st.write(f"**Localisation :** {row.get('location','')}")
                if row.get("description"):
                    st.write(row.get("description"))
                if row.get("requirements"):
                    st.markdown(f"**Exigences :** {row.get('requirements')}")
                if row.get("contact"):
                    st.markdown(f"**Contact :** {row.get('contact')}")
                st.markdown("---")
    with tabs[1]:
        df_h = read_table("housing_ads")
        if df_h.empty:
            st.info("Aucune annonce de logement pour le moment.")
        else:
            city_filter = st.text_input("Filtrer par ville...", key="city_filter")
            df = df_h.copy()
            if city_filter:
                df = df[df["city"].str.contains(city_filter, case=False, na=False)]
            for _, row in df.sort_values("published_at", ascending=False).iterrows():
                st.subheader(f"{row['title']} — {row.get('city','')}")
                st.caption(f"Publié le : {row['published_at']}")
                st.write(f"**Adresse :** {row.get('address','')}")
                st.write(f"**Prix :** {row.get('price','')}")
                if row.get("description"):
                    st.write(row.get("description"))
                if row.get("contact"):
                    st.markdown(f"**Contact :** {row.get('contact')}")
                st.markdown("---")
    with tabs[2]:
        df_t = read_table("trainings")
        if df_t.empty:
            st.info("Aucune formation annoncée pour le moment.")
        else:
            provider_filter = st.text_input("Filtrer par organisme...", key="provider_filter")
            df = df_t.copy()
            if provider_filter:
                df = df[df["provider"].str.contains(provider_filter, case=False, na=False)]
            for _, row in df.sort_values("published_at", ascending=False).iterrows():
                st.subheader(f"{row['title']} — {row.get('provider','')}")
                st.caption(f"Publié le : {row['published_at']}")
                if row.get("start_date"):
                    st.write(f"**Date de début :** {row.get('start_date')}")
                if row.get("duration"):
                    st.write(f"**Durée :** {row.get('duration')}")
                if row.get("description"):
                    st.write(row.get("description"))
                if row.get("contact"):
                    st.markdown(f"**Contact :** {row.get('contact')}")
                st.markdown("---")

# ----------------- Donations -----------------
def donation_page():
    st.header("Soutenir le projet — Faire un don")
    st.info("Les dons ici sont simulés. Pour des paiements réels, intégrer Stripe/PayPal.")
    with st.form("donation_form"):
        donor = st.text_input("Nom (optionnel)")
        amount = st.number_input("Montant (DH)", min_value=1.0, value=50.0, step=5.0, format="%.2f")
        method = st.selectbox("Méthode (simulation)", ["Virement (simulation)", "Espèces", "Carte (simulation)"])
        note = st.text_area("Message / Note (optionnel)")
        submit = st.form_submit_button("Faire un don")
        if submit:
            insert("donations", {
                "donor_name": donor.strip() if donor else "Anonyme",
                "amount": float(amount),
                "method": method,
                "note": note.strip(),
                "donated_at": format_datetime_now()
            })
            st.success(f"Merci pour votre soutien ! (Montant enregistré : {amount} DH)")

    st.subheader("Dons récents")
    df = read_table("donations")
    if df.empty:
        st.write("Aucun don pour le moment.")
    else:
        df_sorted = df.sort_values("donated_at", ascending=False).head(10)
        st.table(df_sorted[["donor_name", "amount", "method", "donated_at"]])

# ----------------- Auth (connexion / inscription) -----------------
def auth_page():
    st.header("🔐 Connexion / Inscription")
    tab1, tab2 = st.tabs(["Se connecter", "Créer un compte"])
    with tab1:
        user = st.text_input("Nom d'utilisateur", key="login_user")
        pwd = st.text_input("Mot de passe", type="password", key="login_pwd")
        if st.button("Connexion"):
            if user.strip() == "" or pwd.strip() == "":
                st.error("Veuillez remplir tous les champs.")
            else:
                with engine.connect() as conn:
                    query = conn.execute(
                        text("SELECT * FROM users WHERE username=:u AND password=:p"),
                        {"u": user, "p": hash_pwd(pwd)}
                    ).fetchone()
                if query:
                    st.success("Connexion réussie ! 🎉")
                    st.session_state["user"] = user
                    # ensure profile exists
                    with engine.begin() as conn:
                        exists = conn.execute(text("SELECT * FROM user_profiles WHERE username=:u"), {"u": user}).fetchone()
                        if not exists:
                            conn.execute(text("INSERT INTO user_profiles(username, created_at) VALUES(:u, :d)"),
                                         {"u": user, "d": format_datetime_now()})
                else:
                    st.error("Nom d'utilisateur ou mot de passe incorrect.")
    with tab2:
        new_user = st.text_input("Créer un nom d'utilisateur", key="reg_user")
        new_pwd = st.text_input("Créer un mot de passe", type="password", key="reg_pwd")
        if st.button("Créer un compte"):
            if new_user.strip() == "" or new_pwd.strip() == "":
                st.error("Veuillez remplir tous les champs.")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(
                            text("INSERT INTO users(username, password) VALUES(:u, :p)"),
                            {"u": new_user, "p": hash_pwd(new_pwd)}
                        )
                        conn.execute(
                            text("INSERT INTO user_profiles(username, created_at) VALUES(:u, :d)"),
                            {"u": new_user, "d": format_datetime_now()}
                        )
                    st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                except Exception:
                    st.error("Nom d'utilisateur déjà utilisé.")

# ----------------- Profile page -----------------
def profile_page():
    st.header("👤 Profil utilisateur")
    if not st.session_state.get("user"):
        st.warning("Veuillez vous connecter pour accéder à votre profil.")
        return
    username = st.session_state["user"]
    st.subheader(f"Bienvenue, {username} !")
    with engine.connect() as conn:
        profile = conn.execute(text("SELECT * FROM user_profiles WHERE username=:u"), {"u": username}).fetchone()
    if profile:
        st.write(f"📅 Date d'inscription : {profile.created_at}")
    st.markdown("### 🔐 Modifier mot de passe")
    new_pwd = st.text_input("Nouveau mot de passe", type="password", key="new_pwd")
    if st.button("Mettre à jour le mot de passe"):
        if new_pwd.strip():
            with engine.begin() as conn:
                conn.execute(text("UPDATE users SET password=:p WHERE username=:u"),
                             {"p": hash_pwd(new_pwd), "u": username})
            st.success("Mot de passe mis à jour !")
    st.markdown("---")
    if st.button("🗑️ Supprimer mon compte"):
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM users WHERE username=:u"), {"u": username})
            conn.execute(text("DELETE FROM user_profiles WHERE username=:u"), {"u": username})
        st.session_state["user"] = None
        st.success("Votre compte a été supprimé.")

# ----------------- Dashboard utilisateur -----------------
def dashboard_page():
    st.header("📊 Tableau de bord")
    if not st.session_state.get("user"):
        st.warning("Veuillez vous connecter pour voir votre tableau de bord.")
        return
    st.subheader(f"Bonjour, {st.session_state['user']} !")
    jobs = read_table("job_offers")
    houses = read_table("housing_ads")
    trainings = read_table("trainings")
    c1, c2, c3 = st.columns(3)
    c1.metric("Offres d'emploi", len(jobs))
    c2.metric("Logements", len(houses))
    c3.metric("Formations", len(trainings))
    st.markdown("### 🔎 Accès rapide")
    r1, r2, r3 = st.columns(3)
    if r1.button("Voir les offres d'emploi"):
        st.session_state["_goto"] = "job"
    if r2.button("Voir les logements"):
        st.session_state["_goto"] = "housing"
    if r3.button("Voir les formations"):
        st.session_state["_goto"] = "training"
    st.markdown("---")
    st.info("Votre tableau de bord sera progressivement enrichi (favoris, historique, notifications).")

# ----------------- Chat communautaire -----------------
def chat_page():
    st.header("💬 Chat - Communauté United Hands")
    if not st.session_state.get("user"):
        st.warning("Veuillez vous connecter pour discuter avec la communauté.")
        return
    username = st.session_state["user"]
    st.subheader("🗨️ Messages récents")
    df = read_table("chat_messages")
    if df.empty:
        st.info("Aucun message pour le moment. Soyez le premier à écrire !")
    else:
        for _, row in df.sort_values("timestamp", ascending=False).head(50).iterrows():
            st.markdown(
                f"**{row['username']}** : {row['message']}  \n"
                f"<span style='font-size:12px;color:gray'>{row['timestamp']}</span>",
                unsafe_allow_html=True
            )
            st.markdown("---")
    st.subheader("✏️ Envoyer un message")
    msg = st.text_input("Votre message", key="chat_msg")
    if st.button("Envoyer"):
        if msg.strip():
            insert("chat_messages", {
                "username": username,
                "message": msg.strip(),
                "timestamp": format_datetime_now()
            })
            st.success("Message envoyé !")
            st.experimental_rerun()

# ----------------- Admin stats and export -----------------
def admin_stats():
    st.header("📈 Statistiques & Administration (Prototype)")
    pwd = st.text_input("Mot de passe administrateur", type="password", key="admin_pwd")
    if pwd != "admin123":
        st.warning("Entrez le mot de passe d'administration pour voir les statistiques.")
        return
    jobs = read_table("job_offers")
    houses = read_table("housing_ads")
    trainings = read_table("trainings")
    donations = read_table("donations")
    col1, col2, col3 = st.columns(3)
    col1.metric("Offres d'emploi", len(jobs))
    col2.metric("Annonces logement", len(houses))
    col3.metric("Formations", len(trainings))
    total_don = donations["amount"].sum() if not donations.empty else 0.0
    st.metric("Total dons (DH)", f"{total_don:.2f}")
    st.subheader("Dons (détail)")
    if not donations.empty:
        st.dataframe(donations.sort_values("donated_at", ascending=False).reset_index(drop=True))
    else:
        st.info("Aucun don enregistré.")
    if st.button("Exporter tout en CSV"):
        jobs.to_csv("job_offers_export.csv", index=False)
        houses.to_csv("housing_ads_export.csv", index=False)
        trainings.to_csv("trainings_export.csv", index=False)
        donations.to_csv("donations_export.csv", index=False)
        st.success("Export CSV créé dans le dossier courant de l'application.")

# ----------------- MAIN -----------------
def main():
    ensure_session()
    init_db()
    banner()
    page = sidebar_navigation()

    # handle quick redirect from home buttons
    if st.session_state.get("_goto") == "job":
        st.session_state["_goto"] = None
        page = "📋 Consulter les annonces"
    elif st.session_state.get("_goto") == "housing":
        st.session_state["_goto"] = None
        page = "📋 Consulter les annonces"
    elif st.session_state.get("_goto") == "training":
        st.session_state["_goto"] = None
        page = "📋 Consulter les annonces"

    if page == "🏠 Accueil":
        home()
    elif page == "📤 Publier une annonce":
        publish_form()
    elif page == "📋 Consulter les annonces":
        view_announcements()
    elif page == "💙 Faire un don":
        donation_page()
    elif page == "📊 Tableau de bord":
        dashboard_page()
    elif page == "👤 Profil":
        profile_page()
    elif page == "💬 Chat":
        chat_page()
    elif page == "🔐 Connexion / Inscription":
        auth_page()
    elif page == "🔎 Statistiques (admin)":
        admin_stats()
    else:
        home()

if __name__ == "__main__":
    main()
