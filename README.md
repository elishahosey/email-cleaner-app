# Email Cleaner

Email Cleaner is a local, interactive Gmail triage dashboard. It shows inbox health, classifies a review sample with transparent rules, and lets you explicitly approve archive or label changes. It never automatically deletes or archives email.

## Current features

- Inbox and unread totals from Gmail
- Full mailbox total and current analysis-coverage progress
- Top senders and category distribution chart
- Deterministic classification by sender, subject, snippet, and Gmail category metadata
- Filterable review queue with sender, subject, date, snippet, category, and suggested action
- Single and bulk selection
- Confirmation before every approved mailbox operation
- Archive (remove `INBOX`, not delete) and apply/create-label actions
- Reversible `Email Cleaner/Delete Candidate` staging and an isolated, typed-confirmation Move to Trash action
- Local JSONL export of messages labeled `TrainingDumpForApp` for future ML work

The queue and category chart review the latest 100 messages across the mailbox, including archived mail and excluding Spam and Trash. Inbox totals still represent the full inbox.

## Setup

### Google OAuth

1. Enable the Gmail API in a Google Cloud project.
2. Configure the OAuth consent screen and add your account as a test user when applicable.
3. Create an OAuth client ID for a Desktop app.
4. Save its JSON as `backend/server/runGmail/credentials.json`.

The existing authentication requests `gmail.readonly`, `gmail.modify`, and the legacy broad `https://mail.google.com/` scope. This version only needs `gmail.modify` (which includes reading and label/archive changes), but retains the existing scope list so current tokens keep working. A future least-privilege migration should remove the broad scope; after changing scopes, delete `backend/server/runGmail/token.json` and sign in again. Both credential files are Git-ignored.

### Backend

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
cd backend
python manage.py migrate
python manage.py runserver
```

On the first dashboard request, OAuth opens a browser and stores the token locally. Port 8080 must be available for its callback.

Copy `backend/backend.env.example` to `backend/backend.env` and replace its Django `SECRET_KEY`. SQLite is the default, so database variables are optional. An explicit local configuration is:

```dotenv
SECRET_KEY=replace-with-a-local-development-key
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_HOST=
DB_PWD=
PORT=
USER=
```

### Start the app

```powershell
cd frontend
npm install
npm start
```

`npm start` uses `backend/.venv` and launches both Django on port 8000 and React on port 3000. Press `Ctrl+C` to stop both. Open `http://localhost:3000`.

To run the processes separately, use `python manage.py runserver` from `backend`, then `npm run start:frontend` from `frontend`. Set `REACT_APP_API_BASE_URL` to override the default `http://localhost:8000/api`.

## Testing

```powershell
cd backend
python manage.py test server.tests

cd ..\frontend
npm test -- --watchAll=false
npm run build
```

Backend tests mock Gmail and never change a mailbox.

### Training export

The dashboard can download `training-dump-for-app.jsonl`. Each line contains one message labeled `TrainingDumpForApp`, including sender, subject, snippet, date, Gmail labels, identifiers for deduplication, the current deterministic `rule_category`, and redacted plain-text body content. Common email addresses, URLs, phone numbers, and long numeric identifiers are replaced with tokens. Bodies are capped at 20,000 characters, and a SHA-256 hash of the unexported original body supports deduplication.

The raw body is never written to the export. Automated redaction is best-effort and cannot guarantee removal of every name, address, medical detail, or other sensitive fact, so inspect the local dataset before using it with any external training provider. Exporting is read-only and does not change Gmail.

## Architecture

- `frontend/src/Intro/`: landing screen
- `frontend/src/BarChart/`: dashboard, preserved Chart.js visualization, review queue, and approval UI
- `backend/server/views.py`: HTTP/JSON boundary
- `backend/server/gmail_client.py`: Gmail reads, label lookup/creation, and batch modification
- `backend/server/classification.py`: pure ordered rules and safe suggestions
- `backend/server/triage_service.py`: aggregation, validation, and approved-action orchestration
- `backend/server/runGmail/emailManage.py`: existing OAuth/service construction and legacy helpers

React requests the dashboard from Django, which calls the triage service and Gmail adapter. Suggestions never mutate Gmail. Only `POST /api/actions/apply` can do so after UI selection and confirmation. Archive removes `INBOX`; labeling adds a label without moving the message.

## Safety model

- Permanent deletion is not exposed. Moving to Gmail Trash is isolated from Archive and requires typing `TRASH` in the UI.
- Refresh and classification never modify Gmail.
- Mailbox changes require selection, an apply click, and browser confirmation.
- Label creation occurs only during an approved label action.
- “Review subscription / unsubscribe” is informational only.

## Roadmap

- Pagination and cached/background refresh for larger inboxes
- Editable personal rules and learned preferences
- Better date normalization, sender grouping, and thread review
- Optional AI classification evaluated against deterministic rules
- Least-privilege OAuth and an explicit sign-in/status flow
- Optional, visually distinct Trash workflow with stronger confirmation (never automatic deletion)
