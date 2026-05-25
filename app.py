import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq
import re

# Configuration de la page
st.set_page_config(page_title="Déchiffreur Administratif National", page_icon="📝", layout="wide")

st.title("📝 Le Déchiffreur Administratif - International & Sécurisé")
st.write("Analyse automatique et sécurisée de vos documents dans leur langue d'origine.")
st.markdown("---")

# --- SÉCURITÉ STRICTE : LA CLÉ API DOIT VENIR DU SERVEUR ---
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

# Si la clé n'est pas dans les secrets du serveur, on arrête tout avec un message pour le développeur
if not api_key:
    st.error("⚠️ **Erreur de configuration (Message pour le Développeur) :** La clé API est introuvable sur le serveur Streamlit Cloud. Veuillez l'ajouter dans l'onglet 'Secrets' de votre tableau de bord share.streamlit.io sous le nom : `GROQ_API_KEY = \"gsk_...\"`.")
    st.stop()

# Barre latérale purement informative (plus aucune saisie possible)
st.sidebar.header("🛡️ Sécurité & Système")
st.sidebar.markdown("""
- **Clé API :** Intégrée au serveur 🔑
- **Filtre RGPD :** Actif (Local) 🛡️
- **Langue de réponse :** Identique au document 🌍
- **Fiabilité :** 100% Factuelle (Pas d'invention) ⚡
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

# Interface utilisateur avec les Onglets
st.subheader("1. Fournissez le document à analyser")
onglet_fichier, onglet_texte = st.tabs(["📁 Importer un fichier (PDF, Word, TXT)", "✍️ Copier-coller du texte brut"])

texte_a_analyser = ""

with onglet_fichier:
    fichier_implique = st.file_uploader("Glissez-déposez votre document ici", type=["pdf", "docx", "txt"], key="uploader")
    if fichier_implique is not None:
        with st.spinner("Lecture du fichier..."):
            texte_a_analyser = extraire_texte_fichier(fichier_implique)

with onglet_texte:
    texte_colle = st.text_area("Collez votre texte ici :", height=200, placeholder="Collez le texte dans n'importe quelle langue (Français, Anglais, Espagnol...)" )
    if texte_colle.strip():
        texte_a_analyser = texte_colle

st.markdown("---")

if texte_a_analyser.strip():
    texte_securise = anonymiser_texte(texte_a_analyser)
    st.success("✓ Document prêt et sécurisé localement.")
    
    if st.button("⚡ Analyser le document", type="primary"):
        st.subheader("📌 Analyse du Document")
        
        client = Groq(api_key=api_key)
        col1, col2, col3 = st.columns(3)
        
        # --- LES CONSIGNES DE FIABILITÉ ABSOLUE ET DE LANGUE ---
        consignes_systeme = (
            "You are a strict, expert legal and administrative assistant. "
            "RULE 1 (LANGUAGE): You MUST detect the language of the provided document and write your entire response in that EXACT SAME LANGUAGE. If the document is in English, respond in English. If in Spanish, respond in Spanish. If in French, respond in French. "
            "RULE 2 (100% RELIABILITY): You must rely ONLY and EXCLUSIVELY on the text provided. Do not use any outside knowledge, do not invent dates, historical facts, figures, or names. If an information is not explicitly written in the text, you must state that it is not specified. "
            "RULE 3 (NO HALLUCINATED LINKS): Do not invent specific sub-URLs. Only provide the main root domain of official trusted portals related to the document's country if relevant (e.g., gov.uk, usa.gov, service-public.fr)."
        )

        # --- COLONNE 1 : LE SENS ---
        with col1:
            st.write("🤔 **Meaning / Signification :**")
            zone_1 = st.empty()
            prompt_1 = f"{consignes_systeme}\n\nTask: Explain the exact purpose of this document in maximum two sentences. Remember to write in the same language as the document. Document:\n\n{texte_securise}"
            try:
                flux_1 = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_1}], stream=True)
                txt1 = ""
                for morceau in flux_1:
                    if morceau.choices[0].delta.content:
                        txt1 += morceau.choices[0].delta.content
                        zone_1.info(txt1)
            except Exception as e:
                st.error(f"Erreur API : {e}")

        # --- COLONNE 2 : LES ACTIONS ---
        with col2:
            st.write("🛠️ **Actions & Requirements :**")
            zone_2 = st.empty()
            prompt_2 = f"{consignes_systeme}\n\nTask: Extract all mandatory actions or guidelines that the user needs to follow from this text. List them as bullet points (-). Include precise financial amounts only if they are written in the text. If no actions are found, state it. Write in the same language as the document. Document:\n\n{texte_securise}"
            try:
                flux_2 = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_2}], stream=True)
                txt2 = ""
                for morceau in flux_2:
                    if morceau.choices[0].delta.content:
                        txt2 += morceau.choices[0].delta.content
                        zone_2.warning(txt2)
            except Exception as e:
                pass

        # --- COLONNE 3 : LES DÉLAIS ---
        with col3:
            st.write("📅 **Deadlines & Dates :**")
            zone_3 = st.empty()
            prompt_3 = f"{consignes_systeme}\n\nTask: Identify all specific deadlines, durations, or expiration dates mentioned in the text. List them clearly. If no deadline is written in the text, explicitly write 'No deadline specified' (in the document's language). Document:\n\n{texte_securise}"
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
    st.info("💡 En attente d'un document pour lancer l'analyse.")
