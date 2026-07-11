import axios from 'axios'

const http = axios.create({ 
  baseURL: 'https://researchgpt-api-3yq6.onrender.com'
})

http.interceptors.request.use((config) => {
  const stored = localStorage.getItem('rg_user')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      const token  = parsed.token || parsed.access_token
      if (token) config.headers.Authorization = `Bearer ${token}`
    } catch (e) {
      console.error('Failed to parse auth token:', e)
    }
  }
  return config
})

export const register = (email, password) => http.post('/auth/register', { email, password })
export const login    = (email, password) => http.post('/auth/login',    { email, password })

export const uploadPaper = (file) => {
  const form = new FormData()
  form.append('file', file)
  return http.post('/papers/upload', form)
}
export const listPapers = () => http.get('/papers/list')

export const createSession = (name) => http.post('/sessions/', { name })
export const listSessions  = ()     => http.get('/sessions/')
export const getHistory    = (id)   => http.get(`/sessions/${id}/history`)
export const deleteSession = (id)   => http.delete(`/sessions/${id}`)

export const askQuestion = (question, paper = null, top_k = 5, session_id = null) =>
  http.post('/qa/ask', { question, paper, top_k, session_id })

export const summarizePaper      = (paper_name)       => http.post('/analysis/summarize',    { paper_name })
export const comparePapers       = (paper_a, paper_b) => http.post('/analysis/compare',      { paper_a, paper_b })
export const generateRelatedWork = (topic)            => http.post('/analysis/related-work', { topic })