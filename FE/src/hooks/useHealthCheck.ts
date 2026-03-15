import { useState, useEffect } from 'react';
import api from '../api';

export const useHealthCheck = () => {
  const [status, setStatus] = useState<'loading' | 'online' | 'offline'>('loading');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        await api.get('/protected/healthcheck');
        setStatus('online');
      } catch (err) {
        setStatus('offline');
      }
    };
    checkStatus();
  }, []);

  return status;
};
