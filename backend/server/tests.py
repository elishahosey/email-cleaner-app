from unittest.mock import ANY, Mock, patch

from django.test import SimpleTestCase

from .classification import classify_email
from .triage_service import apply_approved_action, build_dashboard, validate_action_request
from .training_export import build_training_records, redact_body


class ClassificationTests(SimpleTestCase):
    def test_security_beats_generic_action_language(self):
        result = classify_email({"subject": "Security alert: action required", "sender": "Google", "snippet": ""})
        self.assertEqual(result.category, "Accounts & Security")
        self.assertEqual(result.suggested_action, "Keep visible")

    def test_promotion_uses_gmail_metadata(self):
        result = classify_email({"subject": "Hello", "sender": "Shop", "snippet": "", "label_ids": ["CATEGORY_PROMOTIONS"]})
        self.assertEqual(result.category, "Newsletters / Promotions")
        self.assertEqual(result.suggested_action, "Review subscription / unsubscribe")

    def test_unknown_email_has_safe_no_action_default(self):
        result = classify_email({"subject": "Checking in", "sender": "A friend", "snippet": "Hello"})
        self.assertEqual((result.category, result.suggested_action), ("Other", "No action"))

    def test_receipt_suggests_archive_but_does_not_apply_it(self):
        result = classify_email({"subject": "Your receipt", "sender": "Store", "snippet": ""})
        self.assertEqual((result.category, result.suggested_action), ("Receipts", "Archive"))


class TriageServiceTests(SimpleTestCase):
    @patch("server.triage_service.get_inbox_counts", return_value={"inbox_count": 12, "unread_count": 4})
    @patch("server.triage_service.list_review_messages")
    def test_dashboard_aggregates_review_data(self, list_messages, _counts):
        list_messages.return_value = [
            {"id": "1", "sender": "Store", "subject": "Your order shipped", "snippet": "", "label_ids": []},
            {"id": "2", "sender": "Store", "subject": "Receipt", "snippet": "", "label_ids": []},
        ]
        result = build_dashboard(Mock(), max_results=20)
        self.assertEqual(result["summary"]["inbox_count"], 12)
        self.assertEqual(result["summary"]["top_senders"][0], {"sender": "Store", "count": 2})
        self.assertEqual(result["summary"]["reviewed_count"], 2)

    def test_action_request_rejects_empty_selection(self):
        with self.assertRaisesRegex(ValueError, "Select"):
            validate_action_request({"message_ids": [], "action": "archive"})

    @patch("server.triage_service.modify_messages")
    def test_archive_only_removes_inbox_label(self, modify):
        result = apply_approved_action(Mock(), {"message_ids": ["a", "b"], "action": "archive"})
        modify.assert_called_once_with(ANY, ["a", "b"], remove_label_ids=["INBOX"])
        self.assertEqual(result["updated"], 2)

    @patch("server.triage_service.trash_messages")
    def test_trash_is_a_separate_explicit_action(self, trash):
        service = Mock()
        result = apply_approved_action(service, {"message_ids": ["a"], "action": "trash"})
        trash.assert_called_once_with(service, ["a"])
        self.assertEqual(result, {"updated": 1, "action": "trash", "label": None})

    @patch("server.triage_service.modify_messages")
    @patch("server.triage_service.ensure_label", return_value="Label_123")
    def test_label_is_created_or_found_only_when_apply_runs(self, ensure_label, modify):
        service = Mock()
        apply_approved_action(service, {"message_ids": ["a"], "action": "label", "label_name": "Receipts"})
        ensure_label.assert_called_once_with(service, "Receipts")
        modify.assert_called_once_with(service, ["a"], add_label_ids=["Label_123"])


class TrainingExportTests(SimpleTestCase):
    def test_body_redaction_replaces_common_sensitive_patterns(self):
        redacted, truncated = redact_body(
            "Contact jane@example.com or (512) 555-1212 at https://example.com/a. Account 1234 5678 9012."
        )
        self.assertEqual(
            redacted,
            "Contact <EMAIL> or <PHONE> at <URL> Account <LONG_NUMBER>.",
        )
        self.assertFalse(truncated)

    def test_export_record_contains_portable_labels_and_rule_category(self):
        records = build_training_records([{
            "id": "message-1",
            "thread_id": "thread-1",
            "sender": "Store",
            "sender_email": "store@example.com",
            "subject": "Your receipt",
            "snippet": "Thanks",
            "date": "today",
            "label_ids": ["Label_1", "STARRED"],
            "body": "A useful receipt body",
        }], {"Label_1": "TrainingDumpForApp", "STARRED": "STARRED"})
        self.assertEqual(records[0]["gmail_labels"], ["TrainingDumpForApp", "STARRED"])
        self.assertEqual(records[0]["rule_category"], "Receipts")
        self.assertEqual(records[0]["body_redacted"], "A useful receipt body")
        self.assertEqual(len(records[0]["body_sha256"]), 64)
