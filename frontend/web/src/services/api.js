import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = useAuthStore.getState().getRefreshToken()
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          })
          
          const { access_token, refresh_token } = response.data
          useAuthStore.getState().setTokens(access_token, refresh_token)
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  refresh: () => api.post('/auth/refresh'),
  getMe: () => api.get('/auth/me'),
}

// Export api instance for direct use
export { api }

// User API
export const userApi = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data) => api.put('/users/me', data),
  getPreferences: () => api.get('/users/me/preferences'),
  updatePreferences: (data) => api.put('/users/me/preferences', data),
}

// Portfolio API
export const portfolioApi = {
  getAll: () => api.get('/portfolios'),
  getById: (id) => api.get(`/portfolios/${id}`),
  create: (data) => api.post('/portfolios', data),
  update: (id, data) => api.put(`/portfolios/${id}`, data),
  delete: (id) => api.delete(`/portfolios/${id}`),
  getPerformance: (id) => api.get(`/portfolios/${id}/performance`),
  rebalance: (id) => api.post(`/portfolios/${id}/rebalance`),
  analyze: (data) => api.post('/portfolios/analyze', data),
}

// Analysis API
export const analysisApi = {
  analyzeAssets: (data) => api.post('/analysis/assets', data),
  getSignals: (symbol) => api.get(`/analysis/signals/${symbol}`),
  getExplanation: (portfolioId) => api.get(`/analysis/explain/${portfolioId}`),
  backtest: (data) => api.post('/analysis/backtest', data),
  getModels: () => api.get('/analysis/models'),
}

// Market Data API
export const marketApi = {
  getQuote: (symbol) => api.get(`/market/quote/${symbol}`),
  getBatchQuotes: (symbols) => api.get(`/market/quotes?symbols=${symbols.join(',')}`),
  getPopularStocks: () => api.get('/market/popular'),
  getMarketOverview: () => api.get('/market/overview'),
  searchStocks: (query) => api.get(`/market/search?query=${encodeURIComponent(query)}`),
  getAIAnalysis: (symbol) => api.get(`/market/ai-analysis/${symbol}`),
}

// System API
export const systemApi = {
  getStats: () => api.get('/system/stats'),
}

export default api
