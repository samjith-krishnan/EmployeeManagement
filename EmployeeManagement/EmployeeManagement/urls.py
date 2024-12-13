"""
URL configuration for EmployeeManagement project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from account import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('admin/', admin.site.urls),

    path('dynamic_form/', views.create_form_view, name='create_form'),
    path('form/<int:form_id>/', views.view_dynamic_form, name='view_dynamic_form'),
    path('home',views.Homeview.as_view(),name='home'),
    path('form/<int:id>/responses/', views.FormResponses.as_view(), name='form_responses'),
    path('form/response/delete/<int:id>/<int:form_id>',views.Deletedata.as_view(),name='deletedata'),
    path('form/<int:form_id>/response/update/<int:unique_id>/', views.FieldUpdate.as_view(), name='update_field'),
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path("register/", views.UserCreationView.as_view(), name="register"),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    path('account',views.Accountsection.as_view(),name='account')
]
