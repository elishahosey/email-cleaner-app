"""Business logic for assembling and applying the email review queue."""

from collections import Counter

from .classification import CATEGORIES, classify_email
from .gmail_client import ensure_label, get_inbox_counts, list_review_messages, modify_messages, trash_messages


ALLOWED_ACTIONS = {"keep", "no_action", "archive", "label", "trash"}
MAX_REVIEW_MESSAGES = 100


def build_summary(service):
    return get_inbox_counts(service)


def build_review_queue(service, max_results=MAX_REVIEW_MESSAGES):
    messages = list_review_messages(service, max_results=max_results)
    category_counts = Counter()
    sender_counts = Counter()
    review = []

    for message in messages:
        classification = classify_email(message)
        row = dict(message)
        row.update({
            "category": classification.category,
            "suggested_action": classification.suggested_action,
            "suggested_label": classification.suggested_label,
        })
        review.append(row)
        category_counts[classification.category] += 1
        sender_counts[message["sender"]] += 1

    return {
        "summary": {
            "reviewed_count": len(messages),
            "review_limit": max_results,
            "top_senders": [
                {"sender": sender, "count": count}
                for sender, count in sender_counts.most_common(8)
            ],
            "category_counts": {
                category: category_counts.get(category, 0) for category in CATEGORIES
            },
        },
        "emails": review,
        "categories": list(CATEGORIES),
    }


def build_dashboard(service, max_results=MAX_REVIEW_MESSAGES):
    review = build_review_queue(service, max_results=max_results)
    review["summary"] = {**build_summary(service), **review["summary"]}
    return review


def validate_action_request(payload):
    message_ids = payload.get("message_ids")
    action = payload.get("action")
    if not isinstance(message_ids, list) or not message_ids:
        raise ValueError("Select at least one email.")
    if len(message_ids) > MAX_REVIEW_MESSAGES or not all(isinstance(item, str) and item for item in message_ids):
        raise ValueError("Invalid email selection.")
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Unsupported action.")
    label_name = str(payload.get("label_name", "")).strip()
    if action == "label" and not label_name:
        raise ValueError("A label name is required.")
    return list(dict.fromkeys(message_ids)), action, label_name


def apply_approved_action(service, payload):
    message_ids, action, label_name = validate_action_request(payload)
    if action in {"keep", "no_action"}:
        return {"updated": 0, "action": action}
    if action == "archive":
        modify_messages(service, message_ids, remove_label_ids=["INBOX"])
    elif action == "trash":
        trash_messages(service, message_ids)
    else:
        label_id = ensure_label(service, label_name)
        modify_messages(service, message_ids, add_label_ids=[label_id])
    return {"updated": len(message_ids), "action": action, "label": label_name or None}
