from django.urls import path
from . import views

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('members/', views.member_list, name='member_list'),
    path('members/delete/<int:member_id>/', views.delete_member, name='delete_member'),  # 회원 삭제 URL
    path('bulk_add/', views.bulk_member_add, name='bulk_member_add'),
    path('activities/', views.activity_log, name='activity_log'),
    path('download/', views.download, name='download'),
]
