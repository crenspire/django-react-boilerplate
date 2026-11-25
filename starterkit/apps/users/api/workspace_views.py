from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.views.decorators.http import require_GET
from inertia import render

from apps.users.services.workspace import get_workspace_page


@require_GET
@login_required
def workspace(request: HttpRequest):
    return render(request, "Workspace/Home", get_workspace_page(actor=request.user))
