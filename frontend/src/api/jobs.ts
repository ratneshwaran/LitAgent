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
