import axios from 'axios';

export const getStockData = (symbol) => axios.get(`/api/stock/${symbol}?limit=7`);
export const getDailySummary = (symbol) => axios.get(`/api/stock/${symbol}/daily-summary`);
export const getMetadata = (symbol) => axios.get(`/api/stock/${symbol}/metadata`);
export const populateMetadata = (symbol) => axios.get(`/api/populate-metadata/${symbol}`);


export const getProtectedData = async () => {
  const token = localStorage.getItem('token');
  const res = await axios.get(`/auth/protected`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data;
};
