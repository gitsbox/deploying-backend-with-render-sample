const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { Pool } = require('pg');
const fetch = require('node-fetch');

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(bodyParser.json());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

const BORED_API_BASE_URL = 'https://www.boredapi.com/api/';

app.get('/insert_activity', async (req, res) => {
  try {
    const response = await fetch(BORED_API_BASE_URL + 'activity');
    if (response.ok) {
      const data = await response.json();
      const activity_name = data.activity;
      const query = 'INSERT INTO my_activities (activity) VALUES ($1)';
      await pool.query(query, [activity_name]);
      res.json({
        status: 'success',
        message: `Activity "${activity_name}" inserted successfully`,
      });
    } else {
      res.status(400).json({
        status: 'error',
        message: 'Unable to generate an activity from BoredAPI',
      });
    }
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message,
    });
  }
});

app.get('/', async (req, res) => {
  try {
    const countQuery = 'SELECT COUNT(*) FROM my_activities';
    const countResult = await pool.query(countQuery);
    const count = countResult.rows[0].count;

    const activityQuery = 'SELECT activity FROM my_activities';
    const activityResult = await pool.query(activityQuery);
    const activityNames = activityResult.rows.map((row) => row.activity);

    res.json({
      activity_count: count,
      activities: activityNames,
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message,
    });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
