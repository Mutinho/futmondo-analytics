/**
 * Express server for Futmondo frontend
 * Includes ngrok integration for public access
 */

const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || 'http://localhost:8000';
const NGROK_ENABLED = process.env.NGROK_ENABLED === 'true';
const NGROK_AUTHTOKEN = process.env.NGROK_AUTHTOKEN;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// API proxy - forward requests to backend
app.use('/api', async (req, res, next) => {
  try {
    const axios = require('axios');
    // Preserve /api prefix in the path when forwarding to backend
    const backendPath = `/api${req.path}`;
    const response = await axios({
      method: req.method,
      url: `${API_URL}${backendPath}`,
      data: req.method !== 'GET' ? req.body : undefined,
      headers: {
        'Content-Type': 'application/json',
      },
      params: req.query
    });
    res.json(response.data);
  } catch (error) {
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

// Serve index.html for all routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
const server = app.listen(PORT, async () => {
  console.log(`🚀 Futmondo frontend server running on http://localhost:${PORT}`);
  console.log(`📡 API URL: ${API_URL}`);
  
  // Setup ngrok if enabled
  if (NGROK_ENABLED && NGROK_AUTHTOKEN) {
    try {
      const ngrok = require('@ngrok/ngrok');
      
      // Configure ngrok
      await ngrok.connect({
        addr: PORT,
        authtoken: NGROK_AUTHTOKEN
      }).then(listener => {
        const publicUrl = listener.url();
        console.log('');
        console.log('🌐 ============================================');
        console.log('🌐 ngrok tunnel established!');
        console.log(`🌐 Public URL: ${publicUrl}`);
        console.log('🌐 ============================================');
        console.log('');
      }).catch(err => {
        console.error('❌ Error establishing ngrok tunnel:', err.message);
        console.log('💡 Make sure NGROK_AUTHTOKEN is valid');
      });
    } catch (error) {
      console.error('❌ Error loading ngrok:', error.message);
      console.log('💡 Make sure @ngrok/ngrok is installed: npm install @ngrok/ngrok');
    }
  } else if (NGROK_ENABLED) {
    console.log('⚠️  ngrok is enabled but NGROK_AUTHTOKEN is not set');
    console.log('💡 Set NGROK_AUTHTOKEN in your .env file to enable ngrok');
  }
});

