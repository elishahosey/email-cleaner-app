"""Thin Gmail API adapter. No classification or HTTP concerns belong here."""

import base64
import html
import re
from email.utils import parseaddr

from .runGmail.emailManage import main as build_gmail_service


def get_service():
    return build_gmail_service()


def get_inbox_counts(service):
    profile = service.users().getProfile(userId="me").execute()
    inbox = service.users().labels().get(userId="me", id="INBOX").execute()
    return {
        "account_email": profile.get("emailAddress", ""),
        "total_count": profile.get("messagesTotal", 0),
        "inbox_count": inbox.get("messagesTotal", 0),
        "unread_count": inbox.get("messagesUnread", 0),
    }


def list_review_messages(service, max_results=100):
    """Return recent mailbox messages, including archived mail.

    Spam and Trash are deliberately excluded from the review workflow.
    """
    response = service.users().messages().list(
        userId="me", q="-in:spam -in:trash", maxResults=max_results
    ).execute()
    return _fetch_messages(service, response.get("messages", []))


def list_messages_for_label(service, label_name):
    labels = list_labels(service)
    target = next(
        (label for label in labels if label.get("name", "").casefold() == label_name.casefold()),
        None,
    )
    if not target:
        raise ValueError(f'Gmail label "{label_name}" was not found.')

    message_refs = []
    page_token = None
    while True:
        response = service.users().messages().list(
            userId="me", labelIds=[target["id"]], pageToken=page_token
        ).execute()
        message_refs.extend(response.get("messages", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return _fetch_messages(service, message_refs, include_body=True), {
        label["id"]: label["name"] for label in labels
    }


def _decode_part(part):
    data = part.get("body", {}).get("data")
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="replace")
    except (ValueError, TypeError):
        return ""


def _extract_body(payload):
    plain_parts = []
    html_parts = []

    def walk(part):
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain":
            plain_parts.append(_decode_part(part))
        elif mime_type == "text/html":
            html_parts.append(_decode_part(part))
        for child in part.get("parts", []):
            walk(child)

    walk(payload)
    body = "\n".join(filter(None, plain_parts))
    if not body and html_parts:
        body = re.sub(r"<[^>]+>", " ", "\n".join(html_parts))
        body = html.unescape(body)
    return re.sub(r"\s+", " ", body).strip()


def _fetch_messages(service, message_refs, include_body=False):
    if not message_refs:
        return []

    messages_by_id = {}

    def collect_message(request_id, message, exception):
        if exception is None and message:
            messages_by_id[request_id] = message

    for offset in range(0, len(message_refs), 100):
        batch = service.new_batch_http_request(callback=collect_message)
        for item in message_refs[offset:offset + 100]:
            request = service.users().messages().get(
                userId="me",
                id=item["id"],
                format="full" if include_body else "metadata",
                **({} if include_body else {"metadataHeaders": ["From", "Subject", "Date"]}),
            )
            batch.add(request, request_id=item["id"])
        batch.execute()

    rows = []
    for item in message_refs:
        message = messages_by_id.get(item["id"])
        if not message:
            continue
        headers = {
            header["name"].lower(): header["value"]
            for header in message.get("payload", {}).get("headers", [])
        }
        sender_name, sender_email = parseaddr(headers.get("from", ""))
        row = {
            "id": message["id"],
            "thread_id": message.get("threadId", ""),
            "sender": sender_name or sender_email or headers.get("from", "Unknown sender"),
            "sender_email": sender_email,
            "subject": headers.get("subject", "(no subject)"),
            "date": headers.get("date", ""),
            "snippet": message.get("snippet", ""),
            "label_ids": message.get("labelIds", []),
        }
        if include_body:
            row["body"] = _extract_body(message.get("payload", {}))
        rows.append(row)
    return rows


def list_labels(service):
    return service.users().labels().list(userId="me").execute().get("labels", [])


def ensure_label(service, label_name):
    for label in list_labels(service):
        if label.get("name", "").casefold() == label_name.casefold():
            return label["id"]
    created = service.users().labels().create(
        userId="me",
        body={
            "name": label_name,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        },
    ).execute()
    return created["id"]


def modify_messages(service, message_ids, add_label_ids=None, remove_label_ids=None):
    service.users().messages().batchModify(
        userId="me",
        body={
            "ids": message_ids,
            "addLabelIds": add_label_ids or [],
            "removeLabelIds": remove_label_ids or [],
        },
    ).execute()


def trash_messages(service, message_ids):
    """Move messages to Gmail Trash. This remains reversible in Gmail."""
    batch = service.new_batch_http_request()
    for message_id in message_ids:
        batch.add(
            service.users().messages().trash(userId="me", id=message_id),
            request_id=message_id,
        )
    batch.execute()
