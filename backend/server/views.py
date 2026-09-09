import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .gmail_client import get_service
from .triage_service import (
    apply_approved_action,
    build_dashboard,
    build_review_queue,
    build_summary,
)
from .training_export import TRAINING_LABEL, export_training_jsonl

@require_GET
def dashboard(request):
    try:
        return JsonResponse({"status": "success", **build_dashboard(get_service())})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@require_GET
def summary(request):
    try:
        return JsonResponse({"status": "success", "summary": build_summary(get_service())})
    except Exception as error:
        return JsonResponse({"status": "error", "message": str(error)}, status=500)


@require_GET
def review_queue(request):
    try:
        return JsonResponse({"status": "success", **build_review_queue(get_service())})
    except Exception as error:
        return JsonResponse({"status": "error", "message": str(error)}, status=500)


@require_GET
def export_training_data(request):
    try:
        content, count = export_training_jsonl(get_service())
        response = HttpResponse(content, content_type="application/x-ndjson; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="training-dump-for-app.jsonl"'
        response["X-Exported-Message-Count"] = str(count)
        response["X-Source-Gmail-Label"] = TRAINING_LABEL
        return response
    except ValueError as error:
        return JsonResponse({"status": "error", "message": str(error)}, status=404)
    except Exception as error:
        return JsonResponse({"status": "error", "message": str(error)}, status=500)


@require_POST
def apply_actions(request):
    try:
        payload = json.loads(request.body or "{}")
        result = apply_approved_action(get_service(), payload)
        return JsonResponse({"status": "success", **result})
    except (ValueError, json.JSONDecodeError) as error:
        return JsonResponse({"status": "error", "message": str(error)}, status=400)
    except Exception as error:
        return JsonResponse({"status": "error", "message": str(error)}, status=500)


# Backward-compatible alias for bookmarks/older frontend builds.
run_gmail = dashboard
