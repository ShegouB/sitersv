from traceback import format_tb
from django.db import models
from django.http import JsonResponse
from django.utils.html import format_html

class Participant(models.Model):
    email = models.EmailField(unique=True)
    prenom = models.CharField(max_length=100, blank=True)
    nom = models.CharField(max_length=100, blank=True)
    note_theorique = models.IntegerField(default=0)
    note_pratique = models.IntegerField(default=0)
    a_participe = models.BooleanField(default=False)  # ← nouveau champ
    reponses = models.JSONField(null=True, blank=True)  # Pour stocker les réponses du quiz
    quiz_started = models.BooleanField(default=False)
    cert_generated = models.BooleanField(default=False)

    def resume_reponses(self):
        if not self.reponses:
            return "Aucune réponse"

        html = "<ul>"
        for r in self.reponses:
            q = r.get("question", "???")
            selected = r.get("selected", "❓")
            correct = r.get("correct", "❓")
            etat = "✅" if selected == correct else "❌"
            html += f"<li>{etat} <b>Q:</b> {q[:50]}... <br><b>Réponse choisie:</b> {selected} | <b>Bonne réponse:</b> {correct}</li>"
        html += "</ul>"
        return format_html(html)

    resume_reponses.short_description = "Résumé des réponses"

    @property
    def note_finale(self):
        return round((self.note_theorique + self.note_pratique) / 2, 1)

    def mention(self):
        score = self.note_finale
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Très Bien"
        elif score >= 70:
            return "Bien"
        elif score >= 60:
            return "Assez Bien"
        else:
            return "Insuffisant"
        

class QuizStatus(models.Model):
    start_time = models.DateTimeField(null=True, blank=True)

def get_quiz_time(request):
    status = QuizStatus.objects.first()
    return JsonResponse({"start_time": status.start_time.isoformat() if status.start_time else None})

