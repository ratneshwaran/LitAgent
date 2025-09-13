import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Play, Loader2, AlertCircle } from 'lucide-react'
import { runJob } from '../api/jobs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'

export default function JobForm(){
	const nav = useNavigate()
	const [topic, setTopic] = useState('')
	const [startYear, setStartYear] = useState<number | undefined>()
	const [endYear, setEndYear] = useState<number | undefined>()
	const [include, setInclude] = useState('')
	const [exclude, setExclude] = useState('')
	const [venues, setVenues] = useState('')
	const [limit, setLimit] = useState(20)
	const [provider, setProvider] = useState<'openai'|'anthropic'>('openai')
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState('')

	async function submit(e: React.FormEvent){
		e.preventDefault()
		setError(''); setLoading(true)
		try{
			const job = await runJob(topic, {
				start_year: startYear, end_year: endYear,
				include_keywords: include? include.split(',').map(s=>s.trim()).filter(Boolean):[],
				exclude_keywords: exclude? exclude.split(',').map(s=>s.trim()).filter(Boolean):[],
				venues: venues? venues.split(',').map(s=>s.trim()).filter(Boolean):[],
				limit,
			})
			nav(`/report/${job.job_id}`)
		} catch(e: any){
			setError(e?.message || 'Failed to start job')
		} finally{
			setLoading(false)
		}
	}

	return (
		<Card className="w-full max-w-4xl mx-auto shadow-xl border-0 bg-card/50 backdrop-blur-sm">
			<CardHeader className="text-center pb-6">
				<CardTitle className="text-2xl font-bold">Start Your Literature Review</CardTitle>
				<CardDescription className="text-base">
					Configure your search parameters and let AI analyze the latest research
				</CardDescription>
			</CardHeader>
			
			<CardContent>
				<form onSubmit={submit} className="space-y-6">
					{/* Topic Input */}
					<div className="space-y-2">
						<Label htmlFor="topic" className="text-sm font-medium">
							Research Topic *
						</Label>
						<Input
							id="topic"
							value={topic}
							onChange={e => setTopic(e.target.value)}
							placeholder="e.g., machine learning in healthcare, quantum computing applications"
							required
							className="h-12 text-base"
						/>
					</div>

					{/* Year Range */}
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div className="space-y-2">
							<Label htmlFor="startYear" className="text-sm font-medium">
								Start Year
							</Label>
							<Input
								id="startYear"
								type="number"
								value={startYear ?? ''}
								onChange={e => setStartYear(e.target.value ? Number(e.target.value) : undefined)}
								placeholder="2020"
								min="1900"
								max={new Date().getFullYear()}
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="endYear" className="text-sm font-medium">
								End Year
							</Label>
							<Input
								id="endYear"
								type="number"
								value={endYear ?? ''}
								onChange={e => setEndYear(e.target.value ? Number(e.target.value) : undefined)}
								placeholder={new Date().getFullYear().toString()}
								min="1900"
								max={new Date().getFullYear()}
							/>
						</div>
					</div>

					{/* Keywords and Venues */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
						<div className="space-y-2">
							<Label htmlFor="include" className="text-sm font-medium">
								Include Keywords
							</Label>
							<Input
								id="include"
								value={include}
								onChange={e => setInclude(e.target.value)}
								placeholder="deep learning, neural networks"
							/>
							<p className="text-xs text-muted-foreground">Comma-separated keywords to include</p>
						</div>
						<div className="space-y-2">
							<Label htmlFor="exclude" className="text-sm font-medium">
								Exclude Keywords
							</Label>
							<Input
								id="exclude"
								value={exclude}
								onChange={e => setExclude(e.target.value)}
								placeholder="survey, review"
							/>
							<p className="text-xs text-muted-foreground">Comma-separated keywords to exclude</p>
						</div>
						<div className="space-y-2">
							<Label htmlFor="venues" className="text-sm font-medium">
								Preferred Venues
							</Label>
							<Input
								id="venues"
								value={venues}
								onChange={e => setVenues(e.target.value)}
								placeholder="Nature, NeurIPS, ICML"
							/>
							<p className="text-xs text-muted-foreground">Comma-separated journal/conference names</p>
						</div>
					</div>

					{/* Limit and Provider */}
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div className="space-y-2">
							<Label htmlFor="limit" className="text-sm font-medium">
								Paper Limit
							</Label>
							<Input
								id="limit"
								type="number"
								value={limit}
								onChange={e => setLimit(Number(e.target.value))}
								min="1"
								max="100"
							/>
						</div>
						<div className="space-y-2">
							<Label htmlFor="provider" className="text-sm font-medium">
								AI Provider
							</Label>
							<Select value={provider} onValueChange={(value: 'openai' | 'anthropic') => setProvider(value)}>
								<SelectTrigger>
									<SelectValue />
								</SelectTrigger>
								<SelectContent>
									<SelectItem value="openai">OpenAI GPT</SelectItem>
									<SelectItem value="anthropic">Anthropic Claude</SelectItem>
								</SelectContent>
							</Select>
						</div>
					</div>

					{/* Error Message */}
					{error && (
						<motion.div
							initial={{ opacity: 0, y: -10 }}
							animate={{ opacity: 1, y: 0 }}
							className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 text-destructive border border-destructive/20"
						>
							<AlertCircle className="h-4 w-4" />
							<span className="text-sm">{error}</span>
						</motion.div>
					)}

					{/* Submit Button */}
					<Button
						type="submit"
						disabled={loading || !topic.trim()}
						size="lg"
						className="w-full h-12 text-base font-medium bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5"
					>
						{loading ? (
							<>
								<Loader2 className="mr-2 h-5 w-5 animate-spin" />
								Running Review...
							</>
						) : (
							<>
								<Play className="mr-2 h-5 w-5" />
								Run Literature Review
							</>
						)}
					</Button>
				</form>
			</CardContent>
		</Card>
	)
}
