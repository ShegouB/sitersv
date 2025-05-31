from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from quizp.settings import SECRET_KEY
from .models import Participant
import json
from datetime import datetime

quiz_start_time = None  # Global variable (you can move it to DB or settings later)

@csrf_exempt
def start_quiz_now(request):
    global quiz_start_time
    quiz_start_time = datetime.now()
    return JsonResponse({"status": "Quiz démarré maintenant", "time": quiz_start_time.isoformat()})

@csrf_exempt
def schedule_quiz(request):
    global quiz_start_time
    data = json.loads(request.body)
    quiz_start_time = datetime.fromisoformat(data.get("start_time"))
    return JsonResponse({"status": "Quiz programmé", "time": quiz_start_time.isoformat()})

def get_participants(request):
    data = []
    for p in Participant.objects.all():
        data.append({
            "email": p.email,
            "nom": p.prenom,
            "nom": p.nom,
            "note_theorique": p.note_theorique,
            "note_pratique": p.note_pratique,
            "note_finale": p.note_finale,
            "mention": p.mention(),
            "certificat": p.note_finale >= 60,
        })
    return JsonResponse(data, safe=False)

def update_practical_score(request):
    if request.method == 'POST': # Important de vérifier la méthode
        data = json.loads(request.body)
        email = data.get("email")
        score = data.get("note_pratique") # Le nom du champ doit correspondre à ce que le JS envoie

        if email is None or score is None:
            return JsonResponse({"success": False, "error": "Email ou score manquant."}, status=400)
        
        try:
            score = int(score)
            if not (0 <= score <= 100): # Validation du score
                 return JsonResponse({"success": False, "error": "Score doit être entre 0 et 100."}, status=400)
        except ValueError:
            return JsonResponse({"success": False, "error": "Score doit être un nombre entier."}, status=400)

        try:
            p = Participant.objects.get(email=email)
            p.note_pratique = score
            p.save() # La note_finale sera recalculée grâce à la propriété
            return JsonResponse({
                "success": True, 
                "finale": p.note_finale, # Renvoyer la nouvelle note finale
                "mention": p.mention(),   # Renvoyer la nouvelle mention
                "certificat": p.note_finale >= 60 # Renvoyer le nouveau statut du certificat
            })
        except Participant.DoesNotExist:
            return JsonResponse({"success": False, "error": "Participant non trouvé"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Méthode non autorisée"}, status=405)

from django.http import FileResponse
from .models import Participant
from .utils import generate_certificat_pdf

def download_certificat(request, email):
    try:
        p = Participant.objects.get(email=email)
        if p.note_finale < 60:
            return JsonResponse({"error": "Score insuffisant pour certificat"}, status=403)

        pdf_file = generate_certificat_pdf(p)
        return FileResponse(pdf_file, as_attachment=True, filename=f"certificat_{p.nom}.pdf")
    except Participant.DoesNotExist:
        return JsonResponse({"error": "Participant non trouvé"}, status=404)

from django.contrib.auth import authenticate
from django.http import JsonResponse
import jwt

from dotenv import load_dotenv
load_dotenv()
    
@csrf_exempt
def admin_login(request):
    data = json.loads(request.body)
    user = authenticate(username=data.get("username"), password=data.get("password"))
    if user is not None and user.is_staff:
        token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm="HS256")
        return JsonResponse({"token": token})
    else:
        return JsonResponse({"error": "Identifiants invalides"}, status=401)

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Participant
@csrf_exempt
def verify_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        try:
            p = Participant.objects.get(email=email)
            return JsonResponse({
                "exists": True,
                "is_admin": False,  # utile pour admin check
                "a_participe": p.a_participe
            })
        except Participant.DoesNotExist:
            return JsonResponse({"exists": False})
    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

@csrf_exempt
def save_name(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        nom = data.get("nom")
        prenom = data.get("prenom")

        try:
            participant = Participant.objects.get(email=email)

            # Remplit uniquement s’ils sont vides
            if not participant.nom:
                participant.nom = nom
            if not participant.prenom:
                participant.prenom = prenom

            participant.save()
            return JsonResponse({"success": True})
        except Participant.DoesNotExist:
            return JsonResponse({"error": "Participant introuvable"}, status=404)


from .models import QuizStatus

def get_quiz_time(request):
    try:
        status = QuizStatus.objects.first()
        return JsonResponse({
            "start_time": status.start_time.isoformat() if status and status.start_time else None
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

@csrf_exempt
def submit_quiz(request):
    data = json.loads(request.body)
    email = data.get("email")
    note = data.get("note")
    reponses = data.get("reponses", [])

    try:
        p = Participant.objects.get(email=email)
        if p.a_participe:
            return JsonResponse({"error": "Déjà répondu"}, status=403)
        p.note_theorique = note
        p.reponses = reponses
        p.a_participe = True
        p.save()
        return JsonResponse({"success": True, "finale": p.note_finale})
    except Participant.DoesNotExist:
        return JsonResponse({"error": "Inconnu"}, status=404)


from django.contrib.auth.models import User

@csrf_exempt
def is_admin(request):
    data = json.loads(request.body)
    email = data.get("email")

    # Vérifie d'abord si c'est un User admin
    try:
        user = User.objects.get(email=email)
        return JsonResponse({
            "is_admin": user.is_staff,
            "exists": True,
            "a_participe": False  # on s'en fiche ici
        })
    except User.DoesNotExist:
        pass

    # Sinon, est-ce un Participant ?
    try:
        p = Participant.objects.get(email=email)
        return JsonResponse({
            "is_admin": False,
            "exists": True,
            "a_participe": p.a_participe
        })
    except Participant.DoesNotExist:
        return JsonResponse({
            "is_admin": False,
            "exists": False
        })

        
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def admin_custom(request):
    return render(request, "admin.html")

@csrf_exempt
def get_score_details(request):
    data = json.loads(request.body)
    email = data.get("email")

    try:
        p = Participant.objects.get(email=email)
        return JsonResponse({
            "note_theorique": p.note_theorique,
            "note_pratique": p.note_pratique,
            "note_finale": p.note_finale,
            "mention": p.mention(),
            "certificat": p.note_finale >= 60
        })
    except Participant.DoesNotExist:
        return JsonResponse({"error": "Participant introuvable"}, status=404)


from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.hashers import make_password
from .models import Participant

def public_results_page(request):
    # Cette vue sert simplement le template HTML.
    # Le JavaScript dans result_public.html s'occupera de fetcher les données.
    return render(request, 'quizapp/result_public.html')
