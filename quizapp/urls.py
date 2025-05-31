from django.urls import path
from . import views

urlpatterns = [
    path('api/admin/start-now/', views.start_quiz_now),
    path('api/admin/schedule/', views.schedule_quiz),
    path('api/admin/participants/', views.get_participants),
    path('api/update-score/', views.update_practical_score),
    path('api/admin/certificat/<str:email>/', views.download_certificat),
    path('api/quiz/time/', views.get_quiz_time),
    path('api/verify-email/', views.verify_email),
    path('api/save-name/', views.save_name),
    path('api/submit-quiz/', views.submit_quiz),
    path("api/is-admin/", views.is_admin),
    path('admin-panel/', views.admin_custom, name='admin_custom_panel_url'),
    path('api/certificat/<str:email>/', views.download_certificat),
    path('api/score-details/', views.get_score_details),
    path('results/', views.public_results_page, name='public_results_page'),


]
