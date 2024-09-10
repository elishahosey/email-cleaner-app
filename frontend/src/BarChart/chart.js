import React, { Component } from 'react';
import styles from '../BarChart/chart.module.css';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { useState, useEffect } from 'react'



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

const get_emailDataset = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api');
    return response.data.labels;
  }
  catch (error) {
    console.error('Error getting data:', error);
  }
}

const BarChart = () => {

  const [labelsGmail, setLabelsGmail] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await get_emailDataset();  // Wait for the data
      setLabelsGmail(data);  // Store the data in the state
    };

    fetchData();
  }, []);
  
  const truncateLabel = (label, maxLength = 15) => {
    return label.length > maxLength ? label.slice(0, maxLength) + '...' : label;
  };
  
  const shortenLabels = Object.keys(labelsGmail).map(label => truncateLabel(label));
  

  //TODO: pass data to chart and style it
  const data = {
    labels: shortenLabels,
    datasets: [
      {
        label: 'Your Emails',
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1,
        data: Object.values(labelsGmail),
      },
    ],
  };

  const options = {
    elements: {
      bar: {
        borderRadius: 40,
        borderWidth: 0.7,
      },
    },
    layout: {
      padding: {
        left: 5,
        right: 5,
        top: 10,
        bottom: 5,
      },
      margin: {
        left: 5,
        right: 5,
        top: 5,
        bottom: 5
      }
    },
    scales: {
      y: {
        beginAtZero: true,
      },
      x: {
        beginAtZero: true,
        border: { display: true },
        grid: {
          display: false // No display of grid lines for the x-axis
        },
        ticks: {
          padding: 7
        }
      }
    },
  };

  return (
    <div>
      <Bar data={data} options={options} />
    </div >
  );
};

export default BarChart;