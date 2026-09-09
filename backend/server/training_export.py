"""Create a portable JSONL dataset from explicitly labeled Gmail messages."""

import json
import hashlib
import re

from .classification import classify_email
from .gmail_client import list_messages_for_label


TRAINING_LABEL = "TrainingDumpForApp"
SCHEMA_VERSION = 1
MAX_BODY_CHARS = 20_000

REDACTIONS = (
    (re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE), "<URL>"),
    (re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE), "<EMAIL>"),
    (re.compile(r"(?<!\w)(?:\+?1[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]?\d{4}(?!\w)"), "<PHONE>"),
    (re.compile(r"(?<!\w)(?:\d[ -]?){8,19}(?!\w)"), "<LONG_NUMBER>"),
)


def redact_body(body):
    redacted = body
    for pattern, replacement in REDACTIONS:
        redacted = pattern.sub(replacement, redacted)
    truncated = len(redacted) > MAX_BODY_CHARS
    return redacted[:MAX_BODY_CHARS], truncated


def build_training_records(messages, label_names):
    records = []
    for message in messages:
        classification = classify_email(message)
        raw_body = message.get("body", "")
        redacted_body, body_truncated = redact_body(raw_body)
        records.append({
            "schema_version": SCHEMA_VERSION,
            "gmail_message_id": message["id"],
            "thread_id": message.get("thread_id", ""),
            "sender": message.get("sender", ""),
            "sender_email": message.get("sender_email", ""),
            "subject": message.get("subject", ""),
            "date": message.get("date", ""),
            "snippet": message.get("snippet", ""),
            "body_redacted": redacted_body,
            "body_sha256": hashlib.sha256(raw_body.encode("utf-8")).hexdigest(),
            "body_truncated": body_truncated,
            "gmail_labels": [
                label_names.get(label_id, label_id)
                for label_id in message.get("label_ids", [])
            ],
            "rule_category": classification.category,
        })
    return records


def export_training_jsonl(service):
    messages, label_names = list_messages_for_label(service, TRAINING_LABEL)
    records = build_training_records(messages, label_names)
    content = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
    return content, len(records)
