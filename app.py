import sys
import asyncio

# Correctif obligatoire pour éviter le bug WinError 10054 sur Windows (Local)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq
import re
import easyocr
import numpy as np
from PIL import Image

# Configuration de la page
st.set_page_config(page_title="Déchiffreur Administratif National", page_icon="📝", layout="wide")

st.title("📝 Le Déchiffreur Administratif - Scanner Hybride Local & Cloud")
st.write("Prenez une photo de votre document, importez un fichier ou collez du texte.")
st.markdown("---")

# --- RÉCUPÉRATION DE LA CLÉ API ---
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    st.error("⚠️ **Erreur :** Clé API introuvable. Configurez votre fichier `.streamlit/secrets.toml` en local ou l'onglet 'Secrets' sur le Cloud.")
    st.stop()

# Barre latérale purement informative
st.sidebar.header("🛡️ Spécifications du Système")
st.sidebar.markdown("""
- **Mode :** Grand Public 👥
- **Scanner Photo :** EasyOCR (Local sur votre PC) 🖥️
- **Moteur d'Analyse :** Llama 3.3 70B Versatile 🧠
- **Fiabilité :** 100% Factuelle ⚡
""")

# --- FONCTIONS DE TRAITEMENT ---
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

def extraire_texte_via_vision_locale(image_file):
    """Utilise EasyOCR en local pour lire le texte sur une photo, compatible multilingue"""
    image = Image.open(image_file)
    image_np = np.array(image)
    
    # Configuration du lecteur pour charger le Français, l'Anglais et l'Espagnol
    reader = easyocr.Reader(['fr', 'en', 'es'], gpu=False)
    
    # Lecture du texte
    resultats = reader.readtext(image_np, detail=0)
    
    # Fusion des blocs de texte trouvés
    return "\n".join(resultats)

# --- INTERFACE UTILISATEUR ---
st.subheader("1. Soumettez votre document de la manière la plus simple pour vous")
onglet_photo, onglet_fichier, onglet_texte = st.tabs([
    "📸 Prendre une photo en direct", 
    "📁 Importer un fichier (PDF, Word, Image)", 
    "✍️ Copier-coller du texte"
])

texte_a_analyser = ""

with onglet_photo:
    photo_capturee = st.camera_input("Positionnez le document devant l'appareil et déclenchez :")
    if photo_capturee is not None:
        with st.spinner("👁️ Le scanner local déchiffre les caractères de votre photo..."):
            texte_a_analyser = extraire_texte_via_vision_locale(photo_capturee)

with onglet_fichier:
    fichier_implique = st.file_uploader("Glissez-déposez un fichier :", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    if fichier_implique is not None:
        extension = fichier_implique.name.split(".")[-1].lower()
        if extension in ["png", "jpg", "jpeg"]:
            with st.spinner("👁️ Le scanner local analyse votre image importée..."):
                texte_a_analyser = extraire_texte_via_vision_locale(fichier_implique)
        else:
            with st.spinner("📄 Extraction du texte du fichier..."):
                texte_a_analyser = extraire_texte_fichier(fichier_implique)

with onglet_texte:
    texte_colle = st.text_area("Collez votre texte ici :", height=150)
    if texte_colle.strip():
        texte_a_analyser = texte_colle

st.markdown("---")

# --- MOTEUR D'ANALYSE HAUTE PRÉCISION (LLAMA 3.3 70B) ---
if texte_a_analyser.strip():
    texte_securise = anonymiser_texte(texte_a_analyser)
    st.success("✓ Document converti en texte et sécurisé avec succès.")
    
    with st.expander("🔍 Voir le texte brut extrait par le scanner"):
        st.text(texte_securise)

    if st.button("⚡ Lancer l'analyse haute précision", type="primary"):
        st.subheader("📌 Votre Feuille de Route Clé en Main")
        
        client = Groq(api_key=api_key)
        col1, col2, col3 = st.columns(3)
        
        consignes_systeme = (
            "You are a strict, expert legal and administrative assistant. "
            "RULE 1 (LANGUAGE): Detect the language of the document and write your entire response in that EXACT SAME LANGUAGE. "
            "RULE 2 (100% RELIABILITY): Rely ONLY on the text provided. Do not use outside knowledge. If an info is missing, say it's not specified. "
            "RULE 3 (NO HALLUCINATED LINKS): Only provide the main root domain of official portals if relevant (e.g., service-public.fr, gov.uk)."
        )

        # Utilisation de la version confirmée de ton catalogue : llama-3.3-70b-versatile
        modele_analyse = "llama-3.3-70b-versatile"

        with col1:
            st.write("🤔 **Ce que ça signifie (En clair) :**")
            zone_1 = st.empty()
            prompt_1 = f"{consignes_systeme}\n\nTask: Explain the exact purpose of this document in maximum two sentences. Write in the same language as the document. Document:\n\n{texte_securise}"
            try:
                flux_1 = client.chat.completions.create(model=modele_analyse, messages=[{"role": "user", "content": prompt_1}], stream=True)
                txt1 = ""
                for morceau in flux_1:
                    if morceau.choices[0].delta.content:
                        txt1 += morceau.choices[0].delta.content
                        zone_1.info(txt1)
            except Exception as e:
                st.error(f"Erreur : {e}")

        with col2:
            st.write("🛠️ **Ce que vous devez faire (Actions) :**")
            zone_2 = st.empty()
            prompt_2 = f"{consignes_systeme}\n\nTask: Extract all mandatory actions the user needs to follow as bullet points (-). Include precise money amounts if written. Write in the same language as the document. Document:\n\n{texte_securise}"
            try:
                flux_2 = client.chat.completions.create(model=modele_analyse, messages=[{"role": "user", "content": prompt_2}], stream=True)
                txt2 = ""
                for morceau in flux_2:
                    if morceau.choices[0].delta.content:
                        txt2 += morceau.choices[0].delta.content
                        zone_2.warning(txt2)
            except Exception as e:
                pass

        with col3:
            st.write("📅 **Dates limites & Délais :**")
            zone_3 = st.empty()
            prompt_3 = f"{consignes_systeme}\n\nTask: Identify all specific deadlines or durations. If none, write 'No deadline specified' in the document's language. Document:\n\n{texte_securise}"
            try:
                flux_3 = client.chat.completions.create(model=modele_analyse, messages=[{"role": "user", "content": prompt_3}], stream=True)
                txt3 = ""
                for morceau in flux_3:
                    if morceau.choices[0].delta.content:
                        txt3 += morceau.choices[0].delta.content
                        zone_3.error(txt3)
            except Exception as e:
                pass
else:
    st.info("💡 En attente d'une photo, d'un fichier ou d'un texte pour démarrer.")
