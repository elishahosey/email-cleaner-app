import logo from './logo.svg';
import './App.css';
import Intro from './Intro/introduction';
import BarChart from './BarChart/chart'
import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <div>
  <Routes>
        <Route path='/' element={<Intro />} />
        <Route path='/dashboard' element={<BarChart/>} />
      </Routes>
  </div>
  );
}

export default App;
