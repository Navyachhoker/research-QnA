// src/api/client.js
import axios from 'axios'

// Your backend routes are /sessions/, /papers/, /qa/ etc.
// No /api prefix needed
const http = axios.create({ baseURL: '/' })

http.interceptors.request.use((config) => {
  const stored = localStorage.getItem('rg_user')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      const token  = parsed.token || parsed.access_token
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    } catch (e) {
      console.error('Failed to parse auth token:', e)
    }
  }
  return config
})

// ── Auth ───────────────────────────────────────────────────────────────────────
export const register = (email, password) => http.post('/auth/register', { email, password })
export const login    = (email, password) => http.post('/auth/login',    { email, password })

// ── Papers ─────────────────────────────────────────────────────────────────────
export const uploadPaper = (file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/papers/upload', form)
}
export const listPapers = () => http.get('/papers/list')

// ── Sessions ───────────────────────────────────────────────────────────────────
export const createSession = (name) => http.post('/sessions/', { name })
export const listSessions  = ()     => http.get('/sessions/')
export const getHistory    = (id)   => http.get(`/sessions/${id}/history`)
export const deleteSession = (id)   => http.delete(`/sessions/${id}`)

// ── Q&A ────────────────────────────────────────────────────────────────────────
export const askQuestion = (question, paper = null, top_k = 5, session_id = null) =>
  http.post('/qa/ask', { question, paper, top_k, session_id })

// ── Analysis ───────────────────────────────────────────────────────────────────
export const summarizePaper      = (paper_name)       => http.post('/analysis/summarize',    { paper_name })
export const comparePapers       = (paper_a, paper_b) => http.post('/analysis/compare',      { paper_a, paper_b })
export const generateRelatedWork = (topic)            => http.post('/analysis/related-work', { topic })