import React, { Component } from 'react';
import { Autocomplete, Container, TextField, Typography } from "@mui/material";
import { Box, height } from "@mui/system";
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
    const response = await axios.get('http://localhost:8000/api/rungmail');
    return response.data; //return the whole response
    console.log("Response Data Labels: ", response.data);
    // return response.data.labels;
  }
  catch (error) {
    console.error('Error getting data:', error);
  }
}

const delete_email = async () => {
  try {
    const response = await axios.post('http://localhost:8000/api/deleteEmails',
      { keyword: "category" }
    );
    return response.data;
  }
  catch (error) {
    console.error('Error getting data:', error);
  }
}

const fetch_email = async () => {
  try {
    //TODO: Send additional data with request
    const response = await axios.get('http://localhost:8000/api/emailFetch',
      {
        params:
        {
          keyword: "",
          sender: "clubnews@crunch.com",
          query: ""
        }
      }
    );
    // console.log("Fetch Email Response: ", response.data);
    return response.data;
  }
  catch (error) {
    console.error('Error getting data:', error);
  }
}

const BarChart = () => {

  const [labelsGmail, setLabelsGmail] = useState([]);
  const [senders, setSenders] = useState([]);


  useEffect(() => {
    const fetchData = async () => {
      const data = await get_emailDataset();
      //just grab the labels from the data
      setLabelsGmail(data.labels);
      setSenders(data.senders || []);

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
      <button onClick={delete_email}>Delete Category Emails</button>
      <button onClick={fetch_email}>Fetch Emails</button>
        <Autocomplete
          options={senders}
          getOptionLabel={(option) => option}
          size="small"
          sx={{
            width: 500
          }}
          renderInput={(params) => <TextField {...params} label="Email Senders" />}
        />
    </div >
  );
};

export default BarChart;