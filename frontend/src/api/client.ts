import axios from 'axios'

export const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

export const client = axios.create({
	baseURL: API_BASE,
	timeout: 30000,
})

client.interceptors.response.use(
	(resp) => resp,
	async (error) => {
		// simple retry once on network error
		if (!error.config || error.config.__retried) return Promise.reject(error)
		error.config.__retried = true
		return client.request(error.config)
	}
)
