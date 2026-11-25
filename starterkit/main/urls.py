"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from main.views import home
from apps.admin_panel.api.admin_views import dashboard
from apps.admin_panel.api.auth_views import login_view, logout_view
from apps.admin_panel.api.group_views import (
    group_create,
    group_delete,
    group_edit,
    group_list,
)
from apps.admin_panel.api.user_views import (
    user_create,
    user_delete,
    user_edit,
    user_list,
)
from apps.users.api.role_views import user_role
from apps.users.api.workspace_views import workspace
from apps.budgets.api.client_views import my_requests, request_create, request_edit, request_withdraw
from apps.budgets.api.manager_views import review, review_queue
from apps.budgets.api.admin_views import overview, request_delete

handler403 = "main.views.permission_denied"
handler404 = "main.views.page_not_found"

urlpatterns = [
    path("", home, name="home"),
    path("django-admin/", admin.site.urls),
    path("workspace/", workspace, name="workspace"),
    path("budget/my-requests/", my_requests, name="budget_my_requests"),
    path("budget/my-requests/new/", request_create, name="budget_request_create"),
    path("budget/my-requests/<int:request_id>/edit/", request_edit, name="budget_request_edit"),
    path("budget/my-requests/<int:request_id>/withdraw/", request_withdraw, name="budget_request_withdraw"),
    path("budget/review/", review_queue, name="budget_review_queue"),
    path("budget/review/<int:request_id>/", review, name="budget_review"),
    path("budget/overview/", overview, name="budget_overview"),
    path("budget/overview/<int:request_id>/delete/", request_delete, name="budget_request_delete"),
    # Inertia-powered admin
    path("admin/login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("admin/", dashboard, name="admin_dashboard"),
    path("admin/users/", user_list, name="admin_users"),
    path("admin/users/create/", user_create, name="admin_user_create"),
    path("admin/users/<int:user_id>/edit/", user_edit, name="admin_user_edit"),
    path("admin/users/<int:user_id>/delete/", user_delete, name="admin_user_delete"),
    path("admin/users/<int:user_id>/role/", user_role, name="admin_user_role"),
    path("admin/groups/", group_list, name="admin_groups"),
    path("admin/groups/create/", group_create, name="admin_group_create"),
    path("admin/groups/<int:group_id>/edit/", group_edit, name="admin_group_edit"),
    path("admin/groups/<int:group_id>/delete/", group_delete, name="admin_group_delete"),
]
