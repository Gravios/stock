import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://13.13.13.13',
});

export default apiClient;
