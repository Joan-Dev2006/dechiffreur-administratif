import streamlit as st
import pdfplumber
from docx import Document
from groq import Groq
import re  # Module Python officiel pour la manipulation de texte (Regex)

# Configuration de la page
st.set_page_config(page_title="Déchiffreur Administratif National", page_icon="📝", layout="wide")

st.title("📝 Le Déchiffreur Administratif - Version Sécurisée (RGPD)")
st.write("Analyse anonymisée et conforme pour la protection de vos données personnelles.")
st.markdown("---")

# Barre latérale pour la clé API
st.sidebar.header("🔑 Configuration Cloud")
# L'application va chercher la clé secrète toute seule sur le serveur !
api_key = st.secrets["GROQ_API_KEY"]

st.subheader("1. Importez votre document")
fichier_implique = st.file_uploader("Choisissez un fichier (Format PDF, DOCX ou TXT)", type=["pdf", "docx", "txt"])

# --- LE BOUCLIER DE SÉCURITÉ (ANONYMISATION) ---
def anonymiser_texte(texte_brut):
    """
    Détecte et remplace les données sensibles en local avant l'envoi au Cloud.
    """
    # 1. Masquage des adresses e-mail
    pattern_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    texte_anonyme = re.sub(pattern_email, "[E-MAIL MASQUÉ]", texte_brut)
    
    # 2. Masquage des numéros de téléphone (Formats français standards)
    pattern_telephone = r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}'
    texte_anonyme = re.sub(pattern_telephone, "[TÉLÉPHONE MASQUÉ]", texte_anonyme)
    
    return texte_anonyme

def extraire_texte(fichier):
    extension = fichier.name.split(".")[-1].lower()
    texte = ""
    if extension == "pdf":
        with pdfplumber.open(fichier) as pdf:
            for page in pdf.pages:
                texte += page.extract_text() + "\n"
    elif extension == "docx":
        doc = Document(fichier)
        for para in doc.paragraphs:
            texte += para.text + "\n"
    elif extension == "txt":
        texte = fichier.read().decode("utf-8")
    return texte

st.markdown("---")

if fichier_implique is not None:
    with st.spinner("Extraction du texte intégral..."):
        texte_complet = extraire_texte(fichier_implique)
    
    if not texte_complet.strip():
        st.error("Impossible de lire le texte du document.")
    else:
        # --- Application immédiate du filtre de sécurité en mémoire locale ---
        texte_securise = anonymiser_texte(texte_complet)
        
        st.success(f"✓ Document '{fichier_implique.name}' chargé et sécurisé localement.")
        
        # Affichage transparent pour l'utilisateur
        with st.expander("🔍 Voir les données envoyées de manière sécurisée au Cloud"):
            st.text(texte_securise)

        if st.button("⚡ Déchiffrer en toute sécurité", type="primary"):
            if not api_key:
                st.error("⚠️ Action requise : Veuillez coller votre clé API Groq dans la barre latérale gauche.")
            else:
                st.subheader("📌 Feuille de Route Simplifiée")
                
                client = Groq(api_key=api_key)
                col1, col2, col3 = st.columns(3)
                
                # --- APPEL 1 : SENS (On envoie 'texte_securise') ---
                with col1:
                    st.write("🤔 **Ce que ça veut dire :**")
                    zone_1 = st.empty()
                    with st.spinner("Analyse sémantique..."):
                        prompt_1 = f"Tu es un conseiller juridique expert. Analyse ce document et explique en français très simple, vulgarisé et en deux phrases maximum quel est le but de ce document pour l'utilisateur. Document :\n\n{texte_securise}"
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

                # --- APPEL 2 : ACTIONS ---
                with col2:
                    st.write("🛠️ **Ce que vous devez faire :**")
                    zone_2 = st.empty()
                    with st.spinner("Extraction des obligations..."):
                        prompt_2 = f"Tu es un conseiller juridique expert. Extrais de ce document TOUTES les actions concrètes et obligatoires que l'utilisateur doit accomplir. Liste-les sous forme de puces tirets (-) en français simple. Inclus impérativement les montants précis s'ils existent. Document :\n\n{texte_securise}"
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

                # --- APPEL 3 : DÉLAIS ---
                with col3:
                    st.write("📅 **Date limite :**")
                    zone_3 = st.empty()
                    with st.spinner("Recherche des échéances..."):
                        prompt_3 = f"Tu es un conseiller juridique expert. Analyse ce document et cherche s'il y a des dates limites, des délais maximums ou des durées (ex: 60 jours, 14 jours). Extrais-les de façon très précise sous forme de puces. Si aucun délai n'existe, écris 'Non spécifiée'. Document :\n\n{texte_securise}"
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
    st.info("💡 En attente d'un document pour lancer l'analyse sécurisée.")
