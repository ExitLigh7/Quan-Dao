from django.urls import path, include
from QuanDao_1.academy import views

urlpatterns = [
    path('about/', views.AboutPage.as_view(), name='about'),
    path('classes/', views.ClassesOverviewView.as_view(), name='classes-overview'),
    path('classes/add/', views.ClassCreateView.as_view(), name='class-add'),
    path('classes/<int:pk>/<slug:slug>/', include([
        path('', views.ClassDetailView.as_view(), name='class-detail'),
        path('edit/', views.ClassUpdateView.as_view(), name='class-edit'),
        path('delete/', views.ClassDeleteView.as_view(), name='class-delete'),
        path('enroll/', views.enroll_in_class, name='class-enroll'),
        path('feedback/', views.submit_feedback, name='class-feedback'),
    ])
        ),

    path('schedules/', views.ScheduleListView.as_view(), name='schedule-list'),
    path('schedules/new/', views.ScheduleCreateView.as_view(), name='schedule-create'),
    path('schedules/<int:pk>/', include([
        path('edit/', views.ScheduleUpdateView.as_view(), name='schedule-edit'),
        path('delete/', views.ScheduleDeleteView.as_view(), name='schedule-delete'),
    ])
        ),
]
