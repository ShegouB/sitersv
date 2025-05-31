from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter # On n'utilise plus letter directement
from reportlab.lib.units import inch, mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, gray, darkblue
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
from django.conf import settings
from io import BytesIO
from datetime import datetime

# --- Configuration des Polices (Utilisation directe d'Helvetica) ---
PRIMARY_FONT_REGULAR = 'Helvetica'
PRIMARY_FONT_BOLD = 'Helvetica-Bold'
PRIMARY_FONT_OBLIQUE = 'Helvetica-Oblique' # Pour l'italique
PRIMARY_FONT_BOLD_OBLIQUE = 'Helvetica-BoldOblique' # Pour le gras italique


# --- Couleurs (Identique à avant) ---
COLOR_TEXT_DARK_BLUE = HexColor("#002B4B") 
COLOR_TEXT_REGULAR = HexColor("#2A2A2A")   
COLOR_ACCENT_BLUE = HexColor("#005C9E")    
COLOR_BACKGROUND_BLOCK = HexColor("#002B4B")
COLOR_TEXT_LIGHT = HexColor("#FFFFFF")     
PRIMARY_FONT_SEMIBOLD = 'Helvetica-Bold' 

def generate_certificat_pdf(participant):
    buffer = BytesIO()
    
    # --- TAILLE DE PAGE TYPE POWERPOINT 16:9 (PAYSAGE) ---
    # Dimensions en points (1 inch = 72 points)
    # PowerPoint 16:9 par défaut : 13.333 in (largeur) x 7.5 in (hauteur)
    SLIDE_WIDTH = 13.333 * inch 
    SLIDE_HEIGHT = 7.5 * inch
    pagesize_slide = (SLIDE_WIDTH, SLIDE_HEIGHT) # (960, 540) points

    page_width, page_height = pagesize_slide # page_width > page_height
    c = canvas.Canvas(buffer, pagesize=pagesize_slide)

    # --- Marges (ajustées pour le format paysage) ---
    margin_x = 0.75 * inch 
    margin_y = 0.5 * inch # Marge verticale peut être plus petite en paysage
    
    content_x_start = margin_x
    content_y_start = page_height - margin_y # Y commence en haut
    content_width = page_width - (2 * margin_x)
    
    c.setStrokeColor(COLOR_ACCENT_BLUE)
    c.setLineWidth(1.5) 
    c.rect(margin_x / 2, margin_y / 2, page_width - margin_x, page_height - margin_y)

    # --- Chemins des Images (À ADAPTER ABSOLUMENT - Identique à avant) ---
    try:
        path_logo_rsv_principal = os.path.join(settings.BASE_DIR, 'quizapp', 'static', 'favicon15.png')
        path_logo_rsv_favicon = os.path.join(settings.BASE_DIR, 'quizapp', 'static', 'favicon.png')
        path_signature = os.path.join(settings.BASE_DIR, 'quizapp', 'static', 'code.png')

        logo_rsv_principal_img = ImageReader(path_logo_rsv_principal)
        logo_rsv_favicon_img = ImageReader(path_logo_rsv_favicon)
        signature_img = ImageReader(path_signature)
    except Exception as e:
        print(f"ERREUR: Impossible de charger une ou plusieurs images : {e}")
        logo_rsv_principal_img, logo_rsv_favicon_img, signature_img = None, None, None

    # --- Styles de Paragraphe (Tailles de police peuvent nécessiter un ajustement pour le nouveau format) ---
    # Les tailles de police peuvent être légèrement plus grandes car la largeur est plus importante.
    styles = getSampleStyleSheet()
    style_cert_title_block_line1 = ParagraphStyle(
        'CertTitleBlock1', parent=styles['Normal'], fontName=PRIMARY_FONT_BOLD,
        fontSize=30, leading=30, textColor=COLOR_TEXT_LIGHT, spaceBefore=0, spaceAfter=0 # Plus petit pour tenir
    )
    style_cert_title_block_line2 = ParagraphStyle(
        'CertTitleBlock2', parent=styles['Normal'], fontName=PRIMARY_FONT_BOLD,
        fontSize=30, leading=30, textColor=COLOR_TEXT_LIGHT, leftIndent=0.8 * inch, # Ajuster l'indentation
        spaceBefore=0, spaceAfter=0
    )
    style_participant_name = ParagraphStyle(
        'ParticipantName', parent=styles['Normal'], fontName=PRIMARY_FONT_BOLD,
        fontSize=24, leading=28, textColor=COLOR_TEXT_DARK_BLUE, spaceBefore=0.5 * inch # Moins d'espace
    )
    style_validation_text = ParagraphStyle(
        'ValidationText', parent=styles['Normal'], fontName=PRIMARY_FONT_REGULAR,
        fontSize=10, leading=13, textColor=COLOR_TEXT_REGULAR, spaceBefore=0.2 * inch
    )
    style_quiz_title = ParagraphStyle(
        'QuizTitle', parent=styles['Normal'], fontName=PRIMARY_FONT_SEMIBOLD,
        fontSize=14, leading=18, textColor=COLOR_TEXT_DARK_BLUE, spaceBefore=0.1 * inch
    )
    style_mention_text = ParagraphStyle(
        'MentionText', parent=styles['Normal'], fontName=PRIMARY_FONT_REGULAR,
        fontSize=10, leading=13, textColor=COLOR_TEXT_REGULAR, spaceBefore=0.2 * inch
    )
    style_signature_name = ParagraphStyle(
        'SignatureName', parent=styles['Normal'], fontName=PRIMARY_FONT_REGULAR,
        fontSize=10, leading=13, textColor=COLOR_TEXT_DARK_BLUE, spaceBefore=0.4 * inch
    )
    style_signature_title = ParagraphStyle(
        'SignatureTitle', parent=styles['Normal'], fontName=PRIMARY_FONT_REGULAR,
        fontSize=8, leading=10, textColor=COLOR_TEXT_REGULAR
    )
    style_footer_text = ParagraphStyle(
        'FooterText', parent=styles['Normal'], fontName=PRIMARY_FONT_REGULAR,
        fontSize=7, leading=9, textColor=COLOR_TEXT_REGULAR # Plus petit pour le pied de page
    )

    # === DESSIN DU CERTIFICAT ===

    # --- Logo RSV Principal (en haut à droite) ---
    if logo_rsv_principal_img:
        logo_height = 1.0 * inch # Hauteur du logo principal
        img_w, img_h = logo_rsv_principal_img.getSize()
        aspect = img_w / float(img_h) # Inverser l'aspect si on fixe la hauteur
        logo_width = logo_height * aspect
        c.drawImage(logo_rsv_principal_img, 
                    page_width - margin_x - logo_width, 
                    page_height - margin_y - logo_height, 
                    width=logo_width, height=logo_height, mask='auto')
    
    # --- Bloc Titre "Certificat de réussite" ---
    title_block_line_height = style_cert_title_block_line1.leading # Utiliser le leading pour la hauteur de ligne
    title_block_height_total = title_block_line_height * 2 + 10*mm # Hauteur basée sur 2 lignes + espacement
    title_block_width = 4.5 * inch # Peut-être un peu plus large
    y_title_block_top = content_y_start - (0.5 * inch) # Position Y du HAUT du bloc

    c.setFillColor(COLOR_BACKGROUND_BLOCK)
    c.rect(content_x_start, y_title_block_top - title_block_height_total, title_block_width, title_block_height_total, fill=1, stroke=0)

    # Positionner les lignes de titre à l'intérieur du bloc
    p_title1 = Paragraph("Certificat", style_cert_title_block_line1)
    p_title1.wrapOn(c, title_block_width - 0.2*inch, title_block_line_height)
    p_title1.drawOn(c, content_x_start + 0.1*inch, y_title_block_top - title_block_line_height - (2*mm) ) # Ajuster Y

    p_title2 = Paragraph("de réussite", style_cert_title_block_line2)
    p_title2.wrapOn(c, title_block_width - (style_cert_title_block_line2.leftIndent + 0.2*inch), title_block_line_height)
    p_title2.drawOn(c, content_x_start + 0.1*inch, y_title_block_top - (2*title_block_line_height) - (4*mm) ) # Ajuster Y


    # --- Nom du Participant ---
    # On peut utiliser une plus grande partie de la largeur maintenant
    current_y = y_title_block_top - title_block_height_total - style_participant_name.spaceBefore
    
    p_name = Paragraph(f"{participant.prenom} {participant.nom}", style_participant_name)
    name_w, name_h = p_name.wrapOn(c, content_width * 0.6, 50*mm) # Laisser de la place à droite
    p_name.drawOn(c, content_x_start, current_y - name_h)
    current_y -= (name_h) 


    # --- Texte de validation, Titre du Quiz, Mention ---
    # Ces éléments peuvent être groupés ou distribués différemment
    # Étant donné la largeur, on pourrait les mettre en colonne à droite du nom, ou continuer en dessous.
    # Continuons en dessous pour la simplicité de l'exemple.
    
    current_y -= style_validation_text.spaceBefore # Appliquer l'espace avant le prochain bloc
    p_valid_text = Paragraph("a validé(e) et obtenu le certificat :", style_validation_text)
    valid_w, valid_h = p_valid_text.wrapOn(c, content_width, 20*mm)
    p_valid_text.drawOn(c, content_x_start, current_y - valid_h)
    current_y -= (valid_h)

    current_y -= style_quiz_title.spaceBefore
    quiz_title_text = "Développement Web full Stack"
    p_quiz = Paragraph(quiz_title_text, style_quiz_title)
    quiz_w, quiz_h = p_quiz.wrapOn(c, content_width * 0.7, 30*mm) 
    p_quiz.drawOn(c, content_x_start, current_y - quiz_h)
    current_y -= (quiz_h)

    current_y -= style_mention_text.spaceBefore
    mention_text_full = f"Avec la mention : <b>{participant.mention()}</b>"
    p_mention = Paragraph(mention_text_full, style_mention_text)
    mention_w, mention_h = p_mention.wrapOn(c, content_width, 20*mm)
    p_mention.drawOn(c, content_x_start, current_y - mention_h)
    current_y -= (mention_h)


    # --- Signature et Nom du Signataire ---
    # En raison du format paysage, on peut les placer différemment.
    # Par exemple, signature à gauche, nom/titre à droite, ou tout aligné à gauche mais plus bas.
    # Positionner le bloc signature vers le bas, mais pas tout en bas pour laisser place au footer.
    
    y_signature_block_bottom = margin_y + (1.0 * inch) # Hauteur du bas pour le bloc signature
    
    # Nom et Titre du Signataire (à gauche)
    sig_name_text_x = content_x_start
    p_sig_name = Paragraph("Boris Djagou,", style_signature_name) 
    sig_name_w, sig_name_h = p_sig_name.wrapOn(c, content_width / 3, 20*mm) # Limiter largeur
    p_sig_name.drawOn(c, sig_name_text_x, y_signature_block_bottom + sig_name_h + style_signature_title.leading)

    p_sig_title = Paragraph("CEO of IgbegaX", style_signature_title) 
    sig_title_w, sig_title_h = p_sig_title.wrapOn(c, content_width / 3, 15*mm)
    p_sig_title.drawOn(c, sig_name_text_x, y_signature_block_bottom + sig_name_h)

    # Image de la Signature (au-dessus du nom/titre)
    if signature_img:
        sig_img_height_abs = 0.5 * inch 
        img_w_pts, img_h_pts = signature_img.getSize()
        aspect_sig = img_w_pts / float(img_h_pts)
        sig_img_width_abs = sig_img_height_abs * aspect_sig
        # Positionner la signature au-dessus du texte
        c.drawImage(signature_img, sig_name_text_x, y_signature_block_bottom + sig_name_h + style_signature_title.leading + sig_name_h + (0.1*inch),
                    width=sig_img_width_abs, height=sig_img_height_abs, mask='auto')


    # --- Logo RSV Favicon et Marque (en bas à droite) ---
    if logo_rsv_favicon_img:
        favicon_height = 0.9 * inch  # Hauteur souhaitée pour le logo favicon
        img_w_fav, img_h_fav = logo_rsv_favicon_img.getSize() # Dimensions originales de l'image
        
        # Calculer la largeur en conservant l'aspect ratio basé sur la hauteur souhaitée
        if img_h_fav > 0: # Éviter la division par zéro si l'image a une hauteur nulle
            aspect_fav = img_w_fav / float(img_h_fav)
            favicon_width = favicon_height * aspect_fav
        else:
            favicon_width = favicon_height

        x_logo_favicon = page_width - margin_x - favicon_width 
        # y_logo_favicon sera le point de départ bas du logo
        # y_signature_block_bottom est la hauteur du bas pour le bloc signature, 
        # nous voulons le logo à peu près à la même hauteur ou légèrement au-dessus.
        # Ajustez (favicon_height/3) ou une autre valeur pour un positionnement vertical précis.
        y_logo_favicon = y_signature_block_bottom + (favicon_height / 4) # Essayez d'ajuster ce décalage vertical

        c.drawImage(logo_rsv_favicon_img, 
                    x_logo_favicon, 
                    y_logo_favicon, 
                    width=favicon_width, 
                    height=favicon_height, 
                    mask='auto') # mask='auto' est bon pour la transparence des PNG

    # --- Texte de Pied de Page (Numéro de certificat et Date, en bas à gauche) ---
    cert_id = f"Certificat n° RSV-{participant.id:06}" 
    date_delivrance = f"Délivré le {datetime.now().strftime('%d %B %Y')}"
    footer_line = f"{cert_id}  •  {date_delivrance}" # Utiliser un séparateur
    
    p_footer = Paragraph(footer_line, style_footer_text)
    p_footer.wrapOn(c, content_width / 2, 15*mm) # Limiter la largeur pour le coin gauche
    p_footer.drawOn(c, content_x_start, margin_y + (0.1*inch)) 

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer
