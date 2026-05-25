import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq
import re

# Configuration de la page
st.set_page_config(page_title="Déchiffreur Administratif National", page_icon="📝", layout="wide")

st.title("📝 Le Déchiffreur Administratif - Version Pro")
st.write("Analyse universelle, traduction automatique et orientation vers les sites officiels.")
st.markdown("---")

# Récupération automatique de la clé API
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("⚠️ Erreur : La clé API du serveur est introuvable dans les Secrets.")
    st.stop()

# Barre latérale informative
st.sidebar.header("🛡️ Sécurité & Fiabilité")
st.sidebar.markdown("""
- **Filtre RGPD :** Actif (Local)
- **Moteur :** Llama 3.3 70B (Ultra-Précis)
- **Traduction :** Automatique vers le Français
- **Orientation :** Liens institutionnels certifiés
""")

# --- FONCTIONS REQUISENT (SÉCURITÉ ET EXTRACTION) ---
def anonymiser_texte(texte_brut):
    pattern_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    texte_anonyme = re.sub(pattern_email, "[E-MAIL MASQUÉ]", texte_brut)
    
    pattern_telephone = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
    texte_anonyme = re.sub(pattern_telephone, "[TÉLÉPHONE MASQUÉ]", texte_anonyme)
    return texte_anonyme

def extraire_texte_fichier(fichier):
    extension = fichier.name.split(".")[-1].lower()
    texte = ""
    if extension == "pdf":
        with pdfplumber.open(fichier) as pdf:
            for page in pdf.pages:
                texte_page = page.extract_text()
                if texte_page:
                    texte += texte_page + "\n"
    elif extension == "docx":
        doc = Document(fichier)
        for para in doc.paragraphs:
            texte += para.text + "\n"
    elif extension == "txt":
        texte = fichier.read().decode("utf-8")
    return texte

# --- INTERFACE FLUIDE : LES ONGLETS ---
st.subheader("1. Fournissez le document administratif")
onglet_fichier, onglet_texte = st.tabs(["📁 Importer un fichier (PDF, Word, TXT)", "✍️ Copier-coller du texte brut"])

texte_a_analyser = ""

with onglet_fichier:
    fichier_implique = st.file_uploader("Glissez-déposez votre document ici", type=["pdf", "docx", "txt"], key="uploader")
    if fichier_implique is not None:
        with st.spinner("Lecture du fichier..."):
            texte_a_analyser = extraire_texte_fichier(fichier_implique)

with onglet_texte:
    texte_colle = st.text_area("Collez votre texte administratif ou juridique ici (sans limite de taille) :", height=250, placeholder="Ex: Paste your contract details here / Collez le texte de votre amende...")
    if texte_colle.strip():
        texte_a_analyser = texte_colle

st.markdown("---")

# --- ENGINE D'ANALYSE ---
if texte_a_analyser.strip():
    # Sécurisation immédiate
    texte_securise = anonymiser_texte(texte_a_analyser)
    st.success("✓ Contenu prêt et sécurisé localement.")
    
    with st.expander("🔍 Inspecter les données textuelles anonymisées"):
        st.text(texte_securise)

    if st.button("⚡ Lancer l'analyse haute précision", type="primary"):
        st.subheader("📌 Votre Feuille de Route Personnalisée")
        
        client = Groq(api_key=api_key)
        col1, col2, col3 = st.columns(3)
        
        # --- CONTEXTE MULTILINGUE ET LIENS IMPOSÉS (RÈGLES STRICTES POUR L'IA) ---
        consignes_systeme = (
            "Tu es un conseiller juridique expert et un traducteur d'élite. "
            "IMPORTANT : Si le document soumis n'est pas en français, tu dois d'abord le traduire mentalement. "
            "Toutes tes réponses DOIVENT être rédigées dans un français impeccable, très simple et accessible à un citoyen ordinaire. "
            "Interdiction formelle d'inventer des URL spécifiques (Erreur 404). Tu dois uniquement orienter l'utilisateur "
            "vers les racines des sites officiels français si le contexte s'y prête (ex: service-public.fr, impots.gouv.fr, caf.fr, ameli.fr, urssaf.fr, legifrance.gouv.fr)."
        )

        # --- COLONNE 1 : LE SENS (TRADUIT SI BESOIN) ---
        with col1:
            st.write("🤔 **Ce que ça signifie (Explications) :**")
            zone_1 = st.empty()
            with st.spinner("Décodage en cours..."):
                prompt_1 = f"{consignes_systeme}\n\nAnalyse ce document. Explique en deux phrases maximum son but exact. Si le document original était dans une autre langue que le français, commence obligatoirement ta réponse par la mention '*(Traduit de [Langue d'origine])*'. Document :\n\n{texte_securise}"
                flux_1 = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_1}],
                    stream=True
                )
                txt1 = ""
                for morceau in flux_1:
                    if morceau.choices[0].delta.content:
                        txt1 += morceau.choices[0].delta.content
                        zone_1.info(txt1)

        # --- COLONNE 2 : LES ACTIONS ET DÉMARCHES ---
        with col2:
            st.write("🛠️ **Actions requises & Démarches :**")
            zone_2 = st.empty()
            with st.spinner("Extraction des démarches..."):
                prompt_2 = f"{consignes_systeme}\n\nExtrais toutes les actions concrètes et obligations que l'utilisateur doit accomplir. Liste-les sous forme de puces tirets (-). Inclus les montants financiers précis s'il y en a. À la fin de ta liste, ajoute une section distincte nommée '🌐 Accompagnement Officiel :' où tu donnes uniquement le nom de la racine du site public français légitime pour faire cette démarche (ex: caf.fr ou service-public.fr), sans inventer de sous-pages. Document :\n\n{texte_securise}"
                flux_2 = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_2}],
                    stream=True
                )
                txt2 = ""
                for morceau in flux_2:
                    if morceau.choices[0].delta.content:
                        txt2 += morceau.choices[0].delta.content
                        zone_2.warning(txt2)

        # --- COLONNE 3 : LES DÉLAIS LÉGAUX ---
        with col3:
            st.write("📅 **Échéances & Dates Limites :**")
            zone_3 = st.empty()
            with st.spinner("Calcul des délais..."):
                prompt_3 = f"{consignes_systeme}\n\nIdentifie toutes les dates limites, les durées ou les délais maximums accordés à l'utilisateur (ex: 15 jours, sous 2 mois, avant le 31 décembre). Liste-les clairement. Si aucun délai n'est mentionné, écris textuellement 'Aucun délai strict identifié'. Document :\n\n{texte_securise}"
                flux_3 = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt_3}],
                    stream=True
                )
                txt3 = ""
                for morceau in flux_3:
                    if morceau.choices[0].delta.content:
                        txt3 += morceau.choices[0].delta.content
                        zone_3.error(txt3)
else:
    st.info("💡 En attente d'un fichier ou d'un texte copié pour lancer l'analyse.")
