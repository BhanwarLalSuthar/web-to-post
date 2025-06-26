import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL
console.log(baseURL)
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ||'http://localhost:5000/api' });

export default api;

