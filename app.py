import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq
import re
import os

# Configuration de la page
st.set_page_config(page_title="Déchiffreur Administratif National", page_icon="📝", layout="wide")

st.title("📝 Le Déchiffreur Administratif - Version Pro")
st.write("Analyse universelle, traduction automatique et orientation vers les sites officiels.")
st.markdown("---")

# --- SYSTÈME DE DÉTECTION DE CLÉ ULTRA-ROBUSTE ---
api_key = None

# 1. Tentative via les Secrets Streamlit (Cloud)
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

# 2. Tentative via les Variables d'environnement (Docker / Local)
if not api_key:
    api_key = os.environ.get("GROQ_API_KEY")

# 3. Mode de secours : Si aucune clé n'est trouvée, on remet temporairement la saisie manuelle
if not api_key:
    st.warning("⚙️ Mode Configuration : Aucune clé API automatique détectée sur le serveur.")
    api_key = st.sidebar.text_input("Veuillez coller votre clé API Groq ici pour tester :", type="password")

# Barre latérale informative
st.sidebar.header("🛡️ Sécurité & Fiabilité")
st.sidebar.markdown("""
- **Filtre RGPD :** Actif (Local)
- **Moteur :** Llama 3.3 70B
- **Traduction :** Automatique
""")

def anonymiser_texte(texte_brut):
    pattern_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    texte_anonyme = re.sub(pattern_email, "[E-MAIL MASQUÉ]", texte_brut)
    pattern_telephone = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
    return re.sub(pattern_telephone, "[TÉLÉPHONE MASQUÉ]", texte_anonyme)

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

st.subheader("1. Fournissez le document administratif")
onglet_fichier, onglet_texte = st.tabs(["📁 Importer un fichier (PDF, Word, TXT)", "✍️ Copier-coller du texte brut"])

texte_a_analyser = ""

with onglet_fichier:
    fichier_implique = st.file_uploader("Glissez-déposez votre document ici", type=["pdf", "docx", "txt"], key="uploader")
    if fichier_implique is not None:
        with st.spinner("Lecture du fichier..."):
            texte_a_analyser = extraire_texte_fichier(fichier_implique)

with onglet_texte:
    texte_colle = st.text_area("Collez votre texte administratif ou juridique ici :", height=250)
    if texte_colle.strip():
        texte_a_analyser = texte_colle

st.markdown("---")

if texte_a_analyser.strip():
    texte_securise = anonymiser_texte(texte_a_analyser)
    st.success("✓ Contenu prêt et sécurisé localement.")
    
    if st.button("⚡ Lancer l'analyse haute précision", type="primary"):
        if not api_key:
            st.error("⚠️ Impossible de lancer l'analyse : Clé API manquante.")
        else:
            st.subheader("📌 Votre Feuille de Route Personnalisée")
            client = Groq(api_key=api_key)
            col1, col2, col3 = st.columns(3)
            
            consignes_systeme = (
                "Tu es un conseiller juridique expert. Si le document n'est pas en français, traduis-le. "
                "Réponds en français simple. N'invente JAMAIS d'URL. Donne uniquement des racines de sites officiels (ex: caf.fr)."
            )

            with col1:
                st.write("🤔 **Ce que ça signifie :**")
                zone_1 = st.empty()
                prompt_1 = f"{consignes_systeme}\n\nAnalyse ce document. Explique en deux phrases maximum son but exact. Si le document était étranger, commence par '(Traduit de [Langue])'. Document :\n\n{texte_securise}"
                try:
                    flux_1 = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_1}], stream=True)
                    txt1 = ""
                    for morceau in flux_1:
                        if morceau.choices[0].delta.content:
                            txt1 += morceau.choices[0].delta.content
                            zone_1.info(txt1)
                except Exception as e:
                    st.error(f"Erreur API : {e}")

            with col2:
                st.write("🛠️ **Actions requises :**")
                zone_2 = st.empty()
                prompt_2 = f"{consignes_systeme}\n\nExtrais les actions obligatoires sous forme de puces (-). Inclus les montants. Ajoute une section '🌐 Accompagnement Officiel :' avec la racine du site public adapté. Document :\n\n{texte_securise}"
                try:
                    flux_2 = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_2}], stream=True)
                    txt2 = ""
                    for morceau in flux_2:
                        if morceau.choices[0].delta.content:
                            txt2 += morceau.choices[0].delta.content
                            zone_2.warning(txt2)
                except Exception as e:
                    pass

            with col3:
                st.write("📅 **Échéances :**")
                zone_3 = st.empty()
                prompt_3 = f"{consignes_systeme}\n\nIdentifie les dates limites ou durées. Si rien, écris 'Aucun délai strict identifié'. Document :\n\n{texte_securise}"
                try:
                    flux_3 = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_3}], stream=True)
                    txt3 = ""
                    for morceau in flux_3:
                        if morceau.choices[0].delta.content:
                            txt3 += morceau.choices[0].delta.content
                            zone_3.error(txt3)
                except Exception as e:
                    pass
else:
    st.info("💡 En attente d'un fichier ou d'un texte copié pour lancer l'analyse.")
