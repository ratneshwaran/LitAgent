import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Download, FileText, Code, Table, Calendar, Clock, CheckCircle, XCircle, Loader2, AlertCircle } from 'lucide-react'
import { getResult, pollResult, Job } from '../api/jobs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs'
import Loader from './Loader'
import ErrorBanner from './ErrorBanner'

export default function ReportView(){
	const { jobId } = useParams<{jobId: string}>()
	const [job, setJob] = useState<Job | null>(null)
	const [error, setError] = useState('')
	const [activeTab, setActiveTab] = useState('overview')

	useEffect(()=>{
		if(!jobId) return
		let stop = pollResult(jobId, (j)=> setJob(j))
		return ()=> stop()
	},[jobId])

	useEffect(()=>{ if(job && job.status==='failed') setError(job.message || 'Job failed') },[job])

	if(!job) return <Loader />
	if(job.status==='running') return <Loader />
	if(error) return <ErrorBanner message={error} />

	const downloadFile = (kind: 'md'|'json'|'csv') => {
		const base = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
		window.open(`${base}/download/${job.job_id}/${kind}`, '_blank')
	}

	const getStatusIcon = (status: string) => {
		switch (status.toLowerCase()) {
			case 'completed':
				return <CheckCircle className="h-4 w-4" />
			case 'failed':
				return <XCircle className="h-4 w-4" />
			case 'running':
				return <Loader2 className="h-4 w-4 animate-spin" />
			default:
				return <Clock className="h-4 w-4" />
		}
	}

	const getStatusVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
		switch (status.toLowerCase()) {
			case 'completed':
				return 'default'
			case 'failed':
				return 'destructive'
			case 'running':
				return 'secondary'
			default:
				return 'outline'
		}
	}

	const formatDate = (dateString: string) => {
		const date = new Date(dateString)
		return date.toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		})
	}

	return (
		<div className="min-h-screen py-8">
			<motion.div 
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ duration: 0.6 }}
				className="container mx-auto px-4 space-y-6"
			>
				{/* Header */}
				<Card className="border-0 bg-card/50 backdrop-blur-sm">
					<CardHeader>
						<div className="flex items-start justify-between">
							<div className="flex-1 min-w-0">
								<CardTitle className="text-2xl font-bold mb-2 line-clamp-2">
									{job.topic}
								</CardTitle>
								<div className="flex items-center gap-4 text-sm text-muted-foreground">
									<div className="flex items-center gap-1">
										<Calendar className="h-4 w-4" />
										{formatDate(job.created_at)}
									</div>
									<Badge 
										variant={getStatusVariant(job.status)}
										className="flex items-center gap-1"
									>
										{getStatusIcon(job.status)}
										{job.status}
									</Badge>
									<span>Job ID: {job.job_id.slice(0, 8)}...</span>
								</div>
							</div>
							
							{/* Download Buttons */}
							<div className="flex gap-2">
								<Button
									variant="outline"
									size="sm"
									onClick={() => downloadFile('md')}
									className="flex items-center gap-2"
								>
									<Download className="h-4 w-4" />
									Markdown
								</Button>
								<Button
									variant="outline"
									size="sm"
									onClick={() => downloadFile('json')}
									className="flex items-center gap-2"
								>
									<Download className="h-4 w-4" />
									JSON
								</Button>
								<Button
									variant="outline"
									size="sm"
									onClick={() => downloadFile('csv')}
									className="flex items-center gap-2"
								>
									<Download className="h-4 w-4" />
									CSV
								</Button>
							</div>
						</div>
					</CardHeader>
				</Card>

				{/* Tabs */}
				<Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
					<TabsList className="grid w-full grid-cols-3">
						<TabsTrigger value="overview" className="flex items-center gap-2">
							<FileText className="h-4 w-4" />
							Overview
						</TabsTrigger>
						<TabsTrigger value="details" className="flex items-center gap-2">
							<Table className="h-4 w-4" />
							Details
						</TabsTrigger>
						<TabsTrigger value="raw" className="flex items-center gap-2">
							<Code className="h-4 w-4" />
							Raw JSON
						</TabsTrigger>
					</TabsList>

					<TabsContent value="overview" className="mt-6">
						<Card className="border-0 bg-card/50 backdrop-blur-sm">
							<CardHeader>
								<CardTitle>Literature Review Overview</CardTitle>
								<CardDescription>
									AI-generated summary and analysis of the research papers
								</CardDescription>
							</CardHeader>
							<CardContent>
								{job.markdown_path ? (
									<MarkdownFromUrl jobId={job.job_id} />
								) : (
									<div className="text-center py-12 text-muted-foreground">
										<FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
										<p>No markdown content available</p>
									</div>
								)}
							</CardContent>
						</Card>
					</TabsContent>

					<TabsContent value="details" className="mt-6">
						<Card className="border-0 bg-card/50 backdrop-blur-sm">
							<CardHeader>
								<CardTitle>Detailed Analysis</CardTitle>
								<CardDescription>
									Comprehensive breakdown of papers, methods, and findings
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="text-center py-12 text-muted-foreground">
									<Table className="h-12 w-12 mx-auto mb-4 opacity-50" />
									<p>Detailed analysis view coming soon</p>
									<p className="text-sm">This will show individual paper summaries, comparative analysis, and research gaps</p>
								</div>
							</CardContent>
						</Card>
					</TabsContent>

					<TabsContent value="raw" className="mt-6">
						<Card className="border-0 bg-card/50 backdrop-blur-sm">
							<CardHeader>
								<CardTitle>Raw JSON Data</CardTitle>
								<CardDescription>
									Complete structured data from the literature review process
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="rounded-lg border bg-muted/50 p-4 max-h-[70vh] overflow-auto">
									<pre className="text-sm font-mono whitespace-pre-wrap">
										{job.json_path || 'No JSON data available'}
									</pre>
								</div>
							</CardContent>
						</Card>
					</TabsContent>
				</Tabs>
			</motion.div>
		</div>
	)
}

function MarkdownFromUrl({jobId}:{jobId:string}){
	const [text, setText] = useState<string>('')
	const [loading, setLoading] = useState(true)
	const [error, setError] = useState('')
	
	useEffect(()=>{
		const base = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
		fetch(`${base}/download/${jobId}/md`)
			.then(r => r.text())
			.then(setText)
			.catch(() => setError('Failed to load markdown content'))
			.finally(() => setLoading(false))
	},[jobId])

	if (loading) {
		return (
			<div className="flex items-center justify-center py-12">
				<Loader2 className="h-8 w-8 animate-spin text-primary" />
			</div>
		)
	}

	if (error) {
		return (
			<div className="flex items-center gap-2 p-4 rounded-lg bg-destructive/10 text-destructive border border-destructive/20">
				<AlertCircle className="h-4 w-4" />
				<span>{error}</span>
			</div>
		)
	}

	return (
		<div className="prose prose-sm max-w-none dark:prose-invert">
			<pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
				{text}
			</pre>
		</div>
	)
}
