import { api } from './api';

export const marketplaceService = {
  async categories() {
    const { data } = await api.get('/categories');
    return data;
  },

  async professionals(params?: {
    category_id?: number;
    city?: string;
    min_rating?: number;
    max_price?: number;
    featured?: boolean;
    page?: number;
    limit?: number;
  }) {
    const { data } = await api.get('/professionals', { params });
    return data;
  },

  async professional(id: number) {
    const { data } = await api.get(`/professionals/${id}`);
    return data;
  },

  async reviews(professionalId: number) {
    const { data } = await api.get(`/reviews/professional/${professionalId}`);
    return data;
  },

  async createRequest(payload: {
    category_id: number;
    professional_id?: number;
    title: string;
    description: string;
    location: string;
    budget?: number;
  }) {
    const { data } = await api.post('/requests', payload);
    return data;
  },

  async myRequests() {
    const { data } = await api.get('/requests/me');
    return data;
  },

  async messages(requestId: number) {
    const { data } = await api.get(`/messages/request/${requestId}`);
    return data;
  },

  async sendMessage(payload: { request_id: number; content: string }) {
    const { data } = await api.post('/messages', payload);
    return data;
  },
};
