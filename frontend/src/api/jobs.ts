import { client } from './client'

export type Filters = {
	start_year?: number
	end_year?: number
	include_keywords?: string[]
	exclude_keywords?: string[]
	venues?: string[]
	limit?: number
}

export type Job = {
	job_id: string
	topic: string
	created_at: string
	filters: Filters
	status: 'running' | 'done' | 'failed'
	markdown_path?: string
	json_path?: string
	csv_path?: string
	message?: string
}

export async function runJob(topic: string, filters: Filters) {
	const payload = {
		topic,
		start_year: filters.start_year,
		end_year: filters.end_year,
		include: (filters.include_keywords||[]).join(', '),
		exclude: (filters.exclude_keywords||[]).join(', '),
		venues: (filters.venues||[]).join(', '),
		limit: filters.limit ?? 20,
	}
	const { data } = await client.post<Job>('/run', payload)
	return data
}

export async function getJobs() {
	const { data } = await client.get<Job[]>('/jobs')
	return data
}

export async function getResult(jobId: string) {
	const { data } = await client.get<Job>(`/result/${jobId}`)
	return data
}

export type SearchMode = 'title' | 'semantic' | 'hybrid'

export type SearchResult = {
	id: string
	title: string
	abstract?: string
	authors: string[]
	year?: number
	venue?: string
	doi?: string
	url?: string
	pdf_url?: string
	citations_count?: number
	source: string
	relevance_score: number
	reasons: string[]
}

export type SearchResponse = {
	query: string
	mode: SearchMode
	total_results: number
	papers: SearchResult[]
}

export async function searchPapers(
	query: string,
	mode: SearchMode = 'title',
	k: number = 20,
	filters?: {
		start_year?: number
		end_year?: number
		include_keywords?: string
		exclude_keywords?: string
		venues?: string
		must_have_pdf?: boolean
		oa_only?: boolean
		review_filter?: 'off' | 'soft' | 'hard'
	}
): Promise<SearchResponse> {
	const params = new URLSearchParams({
		q: query,
		mode,
		k: k.toString()
	})

	if (filters) {
		if (filters.start_year) params.append('start_year', filters.start_year.toString())
		if (filters.end_year) params.append('end_year', filters.end_year.toString())
		if (filters.include_keywords) params.append('include_keywords', filters.include_keywords)
		if (filters.exclude_keywords) params.append('exclude_keywords', filters.exclude_keywords)
		if (filters.venues) params.append('venues', filters.venues)
		if (filters.must_have_pdf) params.append('must_have_pdf', 'true')
		if (filters.oa_only) params.append('oa_only', 'true')
		if (filters.review_filter) params.append('review_filter', filters.review_filter)
	}

	const { data } = await client.get<SearchResponse>(`/api/search?${params}`)
	return data
}

export function pollResult(jobId: string, onTick: (job: Job)=>void) {
	let timer: any
	async function tick(){
		try {
			const job = await getResult(jobId)
			onTick(job)
			if (job.status === 'running') timer = setTimeout(tick, 3000)
		} catch(e) {
			timer = setTimeout(tick, 5000)
		}
	}
	tick()
	return ()=> timer && clearTimeout(timer)
}
