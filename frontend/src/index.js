// ============================================================
// index.js — React App Entry Point
// Mounts the root App component into the HTML page.
// ============================================================

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
