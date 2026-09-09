import { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import styles from './chart.module.css';
import dangerStyles from './danger.module.css';
import progressStyles from './progress.module.css';
import { Chart as ChartJS, CategoryScale, LinearScale, BarController, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, BarElement, BarController);
const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';
const DELETE_CANDIDATE_LABEL = 'Email Cleaner/Delete Candidate';
const requestMessage = error => {
  if (!error.response) return 'The backend is offline. Start Django on localhost:8000, then try again.';
  return error.response.data?.message || `Gmail request failed (${error.response.status}).`;
};
const suggestedAction = suggestion => ({ 'Keep visible': 'keep', 'Apply label': 'label', 'Archive': 'archive', 'Review subscription / unsubscribe': 'keep', 'No action': 'no_action' }[suggestion] || 'no_action');

const Dashboard = () => {
  const [data, setData] = useState({ summary: {}, emails: [], categories: [] });
  const [summaryLoading, setSummaryLoading] = useState(true), [queueLoading, setQueueLoading] = useState(true);
  const [error, setError] = useState(''), [notice, setNotice] = useState('');
  const [category, setCategory] = useState('All'), [selected, setSelected] = useState([]);
  const [action, setAction] = useState('archive'), [labelName, setLabelName] = useState('');
  const [applying, setApplying] = useState(false);
  const [exporting, setExporting] = useState(false);

  const loadDashboard = async () => {
    setSummaryLoading(true); setQueueLoading(true); setError(''); setSelected([]);
    const summaryRequest = axios.get(`${API_BASE}/dashboard/summary`)
      .then(response => setData(current => ({ ...current, summary: { ...current.summary, ...response.data.summary } })))
      .catch(e => setError(requestMessage(e)))
      .finally(() => setSummaryLoading(false));
    const queueRequest = axios.get(`${API_BASE}/dashboard/review`)
      .then(response => setData(current => ({ ...current, emails: response.data.emails, categories: response.data.categories, summary: { ...current.summary, ...response.data.summary } })))
      .catch(e => setError(requestMessage(e)))
      .finally(() => setQueueLoading(false));
    await Promise.allSettled([summaryRequest, queueRequest]);
  };
  useEffect(() => { loadDashboard(); }, []);
  const emails = useMemo(() => (data?.emails || []).filter(email => category === 'All' || email.category === category), [data, category]);
  const visibleIds = emails.map(email => email.id);
  const allSelected = visibleIds.length > 0 && visibleIds.every(id => selected.includes(id));
  const toggleAll = () => setSelected(allSelected ? selected.filter(id => !visibleIds.includes(id)) : [...new Set([...selected, ...visibleIds])]);
  const toggleOne = id => setSelected(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id]);
  const loadSuggestion = email => { setSelected([email.id]); setAction(suggestedAction(email.suggested_action)); setLabelName(email.suggested_label || ''); setNotice('Suggestion loaded below. Review it before applying.'); };

  const applyAction = async (requestedAction = action, requestedLabel = labelName.trim()) => {
    if (!selected.length || (requestedAction === 'label' && !requestedLabel)) return;
    if (requestedAction === 'trash') {
      const typed = window.prompt(`Move ${selected.length} selected email(s) to Gmail Trash? This is separate from Archive and remains reversible in Gmail.\n\nType TRASH to continue.`);
      if (typed !== 'TRASH') return;
    } else {
      const prompt = requestedAction === 'archive' ? `Archive ${selected.length} email(s)? They will leave Inbox but will not be deleted.` : requestedAction === 'label' ? `Apply label “${requestedLabel}” to ${selected.length} email(s)? It will be created if needed.` : `Confirm this no-change action for ${selected.length} email(s)?`;
      if (!window.confirm(prompt)) return;
    }
    setApplying(true); setError('');
    try {
      const response = await axios.post(`${API_BASE}/actions/apply`, { message_ids: selected, action: requestedAction, label_name: requestedLabel });
      setNotice(response.data.updated ? `Applied ${requestedAction} to ${response.data.updated} email(s).` : 'Confirmed. No mailbox changes were needed.');
      await loadDashboard();
    } catch (e) { setError(requestMessage(e)); }
    finally { setApplying(false); }
  };

  const exportTrainingData = async () => {
    setExporting(true); setError('');
    try {
      const response = await axios.get(`${API_BASE}/exports/training`, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'training-dump-for-app.jsonl';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setNotice(`Training dataset exported from ${response.headers['x-source-gmail-label'] || 'TrainingDumpForApp'}.`);
    } catch (e) { setError(requestMessage(e)); }
    finally { setExporting(false); }
  };

  const summary = data?.summary || {}, counts = summary.category_counts || {};
  const analyzedCount = summary.reviewed_count || 0;
  const totalCount = summary.total_count || 0;
  const coverage = totalCount ? Math.min(100, Math.round((analyzedCount / totalCount) * 100)) : 0;
  const chartData = { labels: Object.keys(counts), datasets: [{ label: 'Emails in review sample', data: Object.values(counts), backgroundColor: '#55f7d2', borderColor: '#55f7d2', borderWidth: 1 }] };

  return <main className={styles.page}>
    <header className={styles.header}><div><p className={styles.eyebrow}>Personal Gmail triage</p><h1>Email Cleaner</h1><p>{summary.account_email ? `Connected: ${summary.account_email}` : summaryLoading ? 'Connecting to Gmail…' : 'Gmail account unavailable'}</p></div><button className={styles.secondaryButton} onClick={loadDashboard} disabled={summaryLoading || queueLoading}>Refresh</button></header>
    {error && <div className={styles.error}>{error}</div>}{notice && <div className={styles.notice}>{notice}</div>}
    <section className={`${styles.stats} ${progressStyles.summaryGrid}`} aria-label="Mailbox summary"><article><span>Total mail</span><strong>{summaryLoading ? '···' : totalCount.toLocaleString()}</strong><small>All Gmail messages</small></article><article><span>Inbox</span><strong>{summaryLoading ? '···' : summary.inbox_count ?? '—'}</strong></article><article><span>Unread</span><strong>{summaryLoading ? '···' : summary.unread_count ?? '—'}</strong></article><article><span>Analyzed now</span><strong>{queueLoading ? '···' : analyzedCount}</strong><small>{queueLoading ? 'Fetching message metadata' : `Latest ${summary.review_limit || 100} across mail`}</small></article></section>
    <section className={progressStyles.scan} aria-label="Mailbox analysis coverage"><div><span>Mailbox scan coverage</span><strong>{summaryLoading || queueLoading ? 'Calculating' : `${coverage}%`}</strong></div><div className={progressStyles.track} role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={coverage}><span style={{ width: `${coverage}%` }}></span></div><small>{queueLoading || summaryLoading ? 'Synchronizing Gmail metadata…' : `${analyzedCount.toLocaleString()} of ${totalCount.toLocaleString()} messages analyzed in this pass`}</small></section>
    <section className={progressStyles.exportPanel}><div><span>ML dataset</span><strong>TrainingDumpForApp</strong><small>JSONL · redacted body text · SHA-256 body fingerprint · local download</small></div><button onClick={exportTrainingData} disabled={exporting}>{exporting ? 'Exporting…' : 'Export training JSONL'}</button></section>
    <section className={styles.insights}><article className={styles.panel}><h2>Category distribution</h2><div className={styles.chart}><Bar data={chartData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0, color: '#71827f' }, grid: { color: '#263230' } }, x: { ticks: { color: '#71827f' }, grid: { display: false } } } }} /></div></article><article className={styles.panel}><h2>Top senders</h2><ol className={styles.senders}>{(summary.top_senders || []).map(item => <li key={item.sender}><span>{item.sender}</span><strong>{item.count}</strong></li>)}</ol></article></section>
    <section className={styles.panel}>
      <div className={styles.queueHeader}><div><h2>Review queue</h2><p>{queueLoading ? 'Fetching recent mail metadata…' : `${emails.length} email(s) shown · ${selected.length} selected · Spam and Trash excluded`}</p></div><label>Category<select value={category} disabled={queueLoading} onChange={e => { setCategory(e.target.value); setSelected([]); }}><option>All</option>{(data?.categories || []).map(item => <option key={item}>{item}</option>)}</select></label></div>
      <div className={styles.approvalBar}><strong>Approved action</strong><select value={action} onChange={e => setAction(e.target.value)}><option value="keep">Keep visible</option><option value="label">Apply label</option><option value="archive">Archive</option><option value="no_action">No action</option></select>{action === 'label' && <input aria-label="Gmail label name" value={labelName} onChange={e => setLabelName(e.target.value)} placeholder="Label name" />}<button onClick={() => applyAction()} disabled={!selected.length || applying || (action === 'label' && !labelName.trim())}>{applying ? 'Applying…' : `Review & apply (${selected.length})`}</button><small>Archive never deletes mail. No automatic actions are performed.</small></div>
      <div className={dangerStyles.dangerBar}><div><strong>Deletion staging</strong><small>Label candidates first, or explicitly move selected mail to Gmail Trash.</small></div><button className={dangerStyles.candidateButton} onClick={() => { setAction('label'); setLabelName(DELETE_CANDIDATE_LABEL); setNotice('Delete Candidate label loaded above. Review and apply when ready.'); }} disabled={!selected.length || applying}>Prepare candidate label</button><button className={dangerStyles.trashButton} onClick={() => applyAction('trash', '')} disabled={!selected.length || applying}>Move to Trash ({selected.length})</button></div>
      <div className={styles.tableWrap}><table><thead><tr><th><input aria-label="Select all visible emails" type="checkbox" checked={allSelected} disabled={queueLoading} onChange={toggleAll} /></th><th>Sender / email</th><th>Category</th><th>Suggestion</th></tr></thead><tbody>{emails.map(email => <tr key={email.id} className={selected.includes(email.id) ? styles.selected : ''}><td><input aria-label={`Select ${email.subject}`} type="checkbox" checked={selected.includes(email.id)} onChange={() => toggleOne(email.id)} /></td><td><strong>{email.sender}</strong><span className={styles.subject}>{email.subject}</span><span className={styles.snippet}>{email.snippet}</span><time>{email.date}</time></td><td><span className={styles.badge}>{email.category}</span></td><td><button className={styles.suggestion} onClick={() => loadSuggestion(email)}>{email.suggested_action}</button>{email.suggested_label && <small>Label: {email.suggested_label}</small>}</td></tr>)}{queueLoading && <tr><td colSpan="4" className={styles.empty}>Reading Gmail metadata…</td></tr>}{!queueLoading && !emails.length && <tr><td colSpan="4" className={styles.empty}>No mail returned for this account.</td></tr>}</tbody></table></div>
    </section>
  </main>;
};
export default Dashboard;
