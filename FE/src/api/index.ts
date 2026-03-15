import axios from 'axios';

// Dynamically determine the API URL. 
// Since Nginx is proxying /api to the backend, we can use a relative path.
// This ensures it works on admin.dishto.in, ldce.dishto.in, etc.
const api = axios.create({
  baseURL: '/api', 
  withCredentials: true, // Required for HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptors for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Optional: Global error handling (e.g., logging out on 401)
    return Promise.reject(error);
  }
);

export default api;
