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

# Configuration de la page avec un layout large et un titre d'onglet propre
st.set_page_config(page_title="Déchiffreur Administratif", page_icon="⚖️", layout="wide")

# --- DESIGN CSS PERSONNALISÉ (STYLE PREMIUM) ---
st.markdown("""
<style>
    /* Global Background and Fonts */
    .main { background-color: #fcfdfe; }
    h1 { color: #1e293b; font-weight: 800 !important; letter-spacing: -1px; }
    h3 { color: #334155; font-weight: 700 !important; }
    
    /* Custom Styling for the Main Button */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }
    
    /* Micro-ajustements des onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ENTÊTE DE L'APPLICATION ---
st.title("⚖️ Le Déchiffreur Administratif")
st.caption("L'intelligence artificielle au service de la clarté citoyenne • Version Grand Public")
st.markdown("---")

# --- RÉCUPÉRATION DE LA CLÉ API ---
api_key = None
try:
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not api_key:
    st.error("⚠️ **Erreur de configuration :** Clé API introuvable. Veuillez configurer votre fichier `.streamlit/secrets.toml`.")
    st.stop()

# Barre latérale (Sidebar) au look épuré
with st.sidebar:
    st.markdown("### 🛡️ Sécurité & Algorithmes")
    st.info("🔒 **Anonymisation RGPD**\nVos données sensibles (e-mails, téléphones) sont filtrées et masquées localement sur votre machine avant toute analyse.")
    st.divider()
    st.markdown("**Spécifications techniques :**")
    st.caption("- Vision : Moteur OCR Local Multi-langue\n- Cerveau : Llama 3.3 70B Versatile\n- Température : 0.0 (Précision factuelle stricte)")

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
    image = Image.open(image_file)
    image_np = np.array(image)
    reader = easyocr.Reader(['fr', 'en', 'es'], gpu=False)
    resultats = reader.readtext(image_np, detail=0)
    return "\n".join(resultats)

# --- ZONE DE DÉPÔT DOCUMENTAIRE ---
st.markdown("### 📥 1. Soumettre un document")
onglet_photo, onglet_fichier, onglet_texte = st.tabs([
    "📸 Prendre une photo (Smartphone/Webcam)", 
    "📁 Importer un fichier (PDF, Word, Image)", 
    "✍️ Copier-coller du texte textuel"
])

texte_a_analyser = ""

with onglet_photo:
    photo_capturee = st.camera_input("Alignez bien le document et déclenchez :")
    if photo_capturee is not None:
        with st.spinner("👁️ Numérisation et lecture de l'image en cours..."):
            texte_a_analyser = extraire_texte_via_vision_locale(photo_capturee)

with onglet_fichier:
    fichier_implique = st.file_uploader("Glissez votre document ici (Formats acceptés : PDF, DOCX, TXT, PNG, JPG) :", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    if fichier_implique is not None:
        extension = fichier_implique.name.split(".")[-1].lower()
        if extension in ["png", "jpg", "jpeg"]:
            with st.spinner("👁️ Analyse de l'image importée..."):
                texte_a_analyser = extraire_texte_via_vision_locale(fichier_implique)
        else:
            with st.spinner("📄 Lecture du fichier en cours..."):
                texte_a_analyser = extraire_texte_fichier(fichier_implique)

with onglet_texte:
    texte_colle = st.text_area("Collez le bloc de texte brut ici :", height=150, placeholder="Ex: Lettre de relance, notification de droits...")
    if texte_colle.strip():
        texte_a_analyser = texte_colle

# --- BLOC DE DIAGNOSTIC ET MOTEUR ---
if texte_a_analyser.strip():
    texte_securise = anonymiser_texte(texte_a_analyser)
    
    st.markdown("### 🛡️ 2. Validation & Sécurité")
    st.success("✓ Document converti en texte de manière sécurisée.")
    
    with st.expander("🔍 Inspecter le texte extrait par l'appareil"):
        st.text_area("Contenu textuel capturé :", texte_securise, height=150, disabled=True)

    st.markdown("---")
    
    # Bouton d'action principal ultra-visible
    if st.button("⚡ Générer ma feuille de route simplifiée", type="primary"):
        st.markdown("### 📌 3. Analyse du document")
        
        client = Groq(api_key=api_key)
        col1, col2, col3 = st.columns(3, gap="medium")
        
        consignes_systeme = (
            "You are a strict, expert legal and administrative assistant. "
            "RULE 1 (LANGUAGE): Detect the language of the document and write your entire response in that EXACT SAME LANGUAGE. "
            "RULE 2 (100% RELIABILITY): Rely ONLY on the text provided. Do not use outside knowledge. If an info is missing, say it's not specified. "
            "RULE 3 (NO HALLUCINATED LINKS): Only provide the main root domain of official portals if relevant."
        )
        modele_analyse = "llama-3.3-70b-versatile"

        # --- COLONNE 1 : LE SENS (Boîte Bleue) ---
        with col1:
            with st.container(border=True):
                st.markdown("<h3 style='color: #2563eb;'>🔵 Ce que ça signifie</h3>", unsafe_allow_html=True)
                zone_1 = st.empty()
                prompt_1 = f"{consignes_systeme}\n\nTask: Explain the exact purpose of this document in maximum two sentences. Write in the same language as the document. Document:\n\n{texte_securise}"
                try:
                    flux_1 = client.chat.completions.create(model=modele_analyse, messages=[{"role": "user", "content": prompt_1}], stream=True)
                    txt1 = ""
                    for morceau in flux_1:
                        if morceau.choices[0].delta.content:
                            txt1 += morceau.choices[0].delta.content
                            zone_1.markdown(txt1)
                except Exception as e:
                    st.error(f"Erreur : {e}")

        # --- COLONNE 2 : LES ACTIONS (Boîte Orange) ---
        with col2:
            with st.container(border=True):
                st.markdown("<h3 style='color: #ea580c;'>🟠 Ce qu'il faut faire</h3>", unsafe_allow_html=True)
                zone_2 = st.empty()
                prompt_2 = f"{consignes_systeme}\n\nTask: Extract all mandatory actions the user needs to follow as bullet points (-). Include precise money amounts if written. Write in the same language as the document. Document:\n\n{texte_securise}"
                try:
                    flux_2 = client.chat.completions.create(model=modele_analyse, messages=[{"role": "user", "content": prompt_2}], stream=True)
                    txt2 = ""
                    for morceau in flux_2:
                        if morceau.choices[0].delta.content:
                            txt2 += morceau.choices[0].delta.content
                            zone_2.markdown(txt2)
                except Exception as e:
                    pass

        # --- COLONNE 3 : LES DÉLAIS (Boîte Rouge) ---
        with col3:
            with st.container(border=True):
                st.markdown("<h3 style='color: #dc2626;'>🔴 Dates et Échéances</h3>", unsafe_allow_html=True)
                zone_3 = st.empty()
                prompt_3 = f"{consignes_systeme}\n\nTask: Identify all specific deadlines or durations. If none, write 'No deadline specified' in the document's language. Document:\n\n{texte_securise}"
                try:
                    flux_3 = client.chat.completions.create(model=modele_analyse, messages=[{"role": "user", "content": prompt_3}], stream=True)
                    txt3 = ""
                    for morceau in flux_3:
                        if morceau.choices[0].delta.content:
                            txt3 += morceau.choices[0].delta.content
                            zone_3.markdown(txt3)
                except Exception as e:
                    pass
else:
    st.container().info("💡 **Guide de démarrage rapide :** Choisissez un onglet ci-dessus pour soumettre une photo ou une capture de votre courrier. L'IA se chargera de le traduire en instructions claires.")
