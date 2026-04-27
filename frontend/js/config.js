/**
 * config.js
 * Runtime configuration for the frontend.
 *
 * Development: served from http://localhost:3000, backend at localhost:8000.
 * Production (Vercel): set VITE_API_BASE or override window.ACADEMICO_CONFIG
 * in a server-side injected <script> before this file loads.
 *
 * To point to a different backend without editing source, add before the
 * first <script type="module"> in your HTML:
 *   <script>window.ACADEMICO_CONFIG = { API_BASE: 'https://api.yourdomain.com/api' };</script>
 */

export const API_BASE =
  window.ACADEMICO_CONFIG?.API_BASE ?? 'http://localhost:8000/api';
