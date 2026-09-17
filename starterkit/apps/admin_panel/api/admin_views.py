from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.views.decorators.http import require_GET
from inertia import render

from apps.admin_panel.services.dashboard import get_dashboard_page


@require_GET
@login_required
def dashboard(request: HttpRequest):
    return render(request, "Admin/Dashboard", get_dashboard_page(actor=request.user))
