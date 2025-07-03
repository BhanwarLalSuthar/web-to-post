import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
console.log('Axios baseURL:', baseURL);

const api = axios.create({
  baseURL,
});

export default api;
