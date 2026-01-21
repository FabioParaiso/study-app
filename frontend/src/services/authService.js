import api from './api';

export const authService = {
    loginStudent: async (name, password) => {
        const res = await api.post('/login', { name, password });
        return res.data;
    },
    registerStudent: async (name, password) => {
        const res = await api.post('/register', { name, password });
        return res.data;
    }
};
