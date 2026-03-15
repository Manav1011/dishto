import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Required for HttpOnly cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add interceptors for token refresh or error handling if needed later
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If 401 Unauthorized, maybe trigger a refresh token flow
    if (error.response?.status === 401) {
      // Logic for refresh token will go here
    }
    return Promise.reject(error);
  }
);

export default api;
