"""Deterministic email classification rules.

Rules intentionally use only Gmail metadata so classifications are predictable,
fast, and easy to test. Earlier rules have higher priority.
"""

from dataclasses import dataclass


CATEGORIES = (
    "Action Needed",
    "Accounts & Security",
    "Bills / Statements",
    "Pets & Vet",
    "Receipts",
    "Orders & Delivery",
    "Career / Recruiting",
    "Newsletters / Promotions",
    "Housing / Records",
    "Other",
)


@dataclass(frozen=True)
class Classification:
    category: str
    suggested_action: str
    suggested_label: str | None = None


RULES = (
    ("Accounts & Security", ("security alert", "verification code", "verify your", "password", "sign-in", "login", "two-factor", "2fa")),
    ("Bills / Statements", ("bill", "statement", "payment due", "invoice", "balance due", "autopay")),
    ("Pets & Vet", ("veterinary", "veterinarian", " vet ", "pet appointment", "vaccination", "heartworm")),
    ("Receipts", ("receipt", "payment received", "thanks for your purchase", "order confirmation")),
    ("Orders & Delivery", ("shipped", "shipping", "delivery", "delivered", "tracking", "your order")),
    ("Career / Recruiting", ("recruiter", "interview", "application", "job opportunity", "hiring", "candidate")),
    ("Newsletters / Promotions", ("unsubscribe", "newsletter", "sale", "promotion", "promo", "% off", "weekly digest")),
    ("Housing / Records", ("lease", "rent", "property", "mortgage", "tenant", "maintenance request", "document available")),
    ("Action Needed", ("action required", "action needed", "please respond", "response required", "urgent", "deadline")),
)


def classify_email(email: dict) -> Classification:
    text = " ".join(
        str(email.get(field, "")) for field in ("sender", "subject", "snippet")
    ).lower()
    gmail_labels = {label.upper() for label in email.get("label_ids", [])}

    for category, keywords in RULES:
        if any(keyword in text for keyword in keywords):
            if category == "Newsletters / Promotions":
                return Classification(category, "Review subscription / unsubscribe", category)
            if category == "Action Needed" or category == "Accounts & Security":
                return Classification(category, "Keep visible", category)
            if category == "Receipts":
                return Classification(category, "Archive")
            return Classification(category, "Apply label", category)

    if "CATEGORY_PROMOTIONS" in gmail_labels:
        category = "Newsletters / Promotions"
        return Classification(category, "Review subscription / unsubscribe", category)

    return Classification("Other", "No action")
