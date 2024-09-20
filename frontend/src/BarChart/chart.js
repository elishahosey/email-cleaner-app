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

const handleBarClick = (event, elements) => {
 console.log("ELEMENTS",elements)
}

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

  //TODO: Make chart bars clickable for further analysis
  const options = {
    events: ['click'],
    elements: {
      bar: {
        borderRadius: 40,
        borderWidth: 0.7,
      },
    },
    onClick: (event,chart)=> {
      chart = ChartJS.instances
      if(chart){
        // get element from coordinates and metaset
        const xClick = event.native.offsetX
        const yClick = event.native.offsetY
        const meta = chart.getDatasetMeta(0)
        console.log("XCLICK: ",xClick)
        console.log("EVENT: ",event)
        console.log("CHART: ",chart)
        console.log("META: ",meta)

      }else{
        console.log("Chart does not exist")
      }
      // Get the elements that were clicked
      // const elements = chartInstance.getElementsAtEventForMode(event, 'nearest', { intersect: true }, false);
      
    //   if (elements.length) {
    //     console.log('Clicked Element:', elements[0]);
    //   } else {
    //     console.log('No element clicked');
    // }
  },
    // onClick: (e)=> handleBarClick(e,elements),
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