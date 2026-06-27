import { api } from './api';

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  name: string;
  email: string;
  password: string;
  role: 'client' | 'professional';
};

export const authService = {
  async login(payload: LoginPayload) {
    const { data } = await api.post('/auth/login', payload);
    localStorage.setItem('@bellora:token', data.access_token);
    localStorage.setItem('@bellora:user', JSON.stringify(data.user));
    return data;
  },

  async register(payload: RegisterPayload) {
    const { data } = await api.post('/auth/register', payload);
    localStorage.setItem('@bellora:token', data.access_token);
    localStorage.setItem('@bellora:user', JSON.stringify(data.user));
    return data;
  },

  async me() {
    const { data } = await api.get('/auth/me');
    return data;
  },

  logout() {
    localStorage.removeItem('@bellora:token');
    localStorage.removeItem('@bellora:user');
  },
};
