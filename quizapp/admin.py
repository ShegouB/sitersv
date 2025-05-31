from django.contrib import admin
from .models import Participant, QuizStatus

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = (
        "email", "prenom", "nom", 
        "note_theorique", "note_pratique", # note_pratique est ici
        "note_finale", "a_participe" # J'ai ajouté resume_reponses pour la cohérence
    )
    search_fields = ("email", "nom", "prenom") # Utile pour rechercher
    list_filter = ("a_participe",) # Utile pour filtrer
    list_per_page = 1
    # Les champs qui sont en lecture seule
    readonly_fields = ("note_finale",)

    # Définition des sections dans le formulaire d'édition/création
    fieldsets = (
        ("Informations du Participant", { # Un titre pour la section
            "fields": (
                "email", 
                "nom", 
                "prenom", 
                "a_participe" # Si tu veux pouvoir le modifier manuellement
            )
        }),
        ("Scores", { # Une section dédiée aux scores
            "fields": (
                "note_theorique", # Devrait être éditable
                "note_pratique",  # Devrait être éditable
                "note_finale"     # Sera en lecture seule car dans readonly_fields
            )
        }),
        
    )



@admin.register(QuizStatus)
class QuizStatusAdmin(admin.ModelAdmin):
    list_display = ("start_time",)
