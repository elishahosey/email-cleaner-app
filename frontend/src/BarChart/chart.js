import React, { Component } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';



import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarController,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  BarController
);

const get_emailDataset = async () =>{
  try {
    const response = await axios.get('http://localhost:8000/api');
    // console.log(response.data); // Print the JSON response from the server
}
  catch (error) {
    console.error('Error getting data:', error);
  }
}

const BarChart = () => {

  get_emailDataset();

  //TODO: pass data to chart
    const data = {
      labels: ['Label 1', 'Label 2', 'Label 3', 'Label 4', 'Label 5'],
      datasets: [
        {
          label: 'Data Series 1',
          backgroundColor: 'rgba(75, 192, 192, 0.6)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1,
          data: [12, 19, 3, 5, 2],
        },
      ],
    };
  
    const options = {
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    };
  
    return (
      <div>
        <Bar data={data} options={options} />
      </div>
    );
  };
  
  export default BarChart;