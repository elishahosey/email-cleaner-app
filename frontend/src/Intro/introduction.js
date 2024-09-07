import styles from '../Intro/introduction.module.css'
import axios from 'axios';
import { useNavigate } from 'react-router-dom'

function Intro() {

  const navigate = useNavigate();
  const sendToLogin = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api');
      console.log(response.data); // Print the JSON response from the server
      navigate('/dashboard');
  }
    catch (error) {
      console.error('Error running script:', error);
    }
  }


  return (
    <div>
      <span>Welcome to the Email Cleaner</span>
      <button onClick={sendToLogin}>Start</button>
    </div>
  );
}

export default Intro;