import styles from './introduction.module.css';
import { useNavigate } from 'react-router-dom'

function Intro() {

  const navigate = useNavigate();
  const sendToLogin = async () => {
    try {
      // const response = await axios.post('http://localhost:8000/api/');
      // console.log(response.data); // Print the JSON response from the server
      navigate('/dashboard');
  }
    catch (error) {
      console.error('Error running script:', error);
    }
  }


  return <main className={styles.page}>
    <nav className={styles.nav}><span className={styles.brand}><span className={styles.mark}>E</span>Mail Control</span><span className={styles.private}>Personal instance · Localhost</span></nav>
    <section className={styles.hero}>
      <div className={styles.copy}>
        <p className={styles.eyebrow}>Personal Gmail utility</p>
        <h1>Inbox triage console.</h1>
        <p className={styles.lede}>Scan the latest inbox messages, sort them with local rules, then decide what to archive or label.</p>
        <button className={styles.start} onClick={sendToLogin}>Enter console <span aria-hidden="true">→</span></button>
        <p className={styles.reassurance}>Mailbox writes require your approval. Delete is disabled.</p>
      </div>
      <div className={styles.preview} aria-label="Console workflow">
        <div className={styles.previewTop}><span></span><span></span><span></span><strong>Session procedure</strong></div>
        <div className={styles.miniStats}><article><small>Utility</small><b>EC/TRIAGE</b></article><article><small>Mode</small><b>Manual</b></article></div>
        <div className={styles.miniQueue}><p><i className={styles.purple}></i><span><b>01 / Scan</b><small>Read up to 100 recent inbox messages</small></span></p><p><i className={styles.green}></i><span><b>02 / Classify</b><small>Apply deterministic local rules</small></span></p><p><i className={styles.orange}></i><span><b>03 / Review</b><small>Wait for selection and approval</small></span></p></div>
      </div>
    </section>
    <section className={styles.features}><article><span>READ</span><h2>Inbox metadata</h2><p>Sender, subject, snippet, date, labels, and summary counts.</p></article><article><span>WRITE</span><h2>Approval required</h2><p>Archive and label actions run only after explicit confirmation.</p></article><article><span>DELETE</span><h2>Disabled</h2><p>This utility does not automatically trash or permanently delete mail.</p></article></section>
  </main>;
}

export default Intro;
