import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

export const api = {
    searchMovies: async (query) => {
        const response = await axios.get(`${API_BASE_URL}/search`, { params: { q: query } });
        return response.data;
    },

    identifyTheme: async (history) => {
        const response = await axios.post(`${API_BASE_URL}/identify_theme`, { history });
        return response.data;
    },

    getRecommendations: async (themeDetail) => {
        const response = await axios.post(`${API_BASE_URL}/recommend`, { theme_detail: themeDetail });
        return response.data;
    }
};
