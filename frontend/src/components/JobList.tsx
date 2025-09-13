import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Calendar, Clock, CheckCircle, XCircle, Loader2, ExternalLink, FileText } from 'lucide-react'
import { getJobs, Job } from '../api/jobs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

export default function JobList(){
	const [jobs, setJobs] = useState<Job[]>([])
	const [loading, setLoading] = useState(true)
	
	useEffect(() => { 
		getJobs()
			.then(setJobs)
			.catch(() => {})
			.finally(() => setLoading(false))
	}, [])

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
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit'
		})
	}

	if (loading) {
		return (
			<div className="flex items-center justify-center py-12">
				<Loader2 className="h-8 w-8 animate-spin text-primary" />
			</div>
		)
	}

	if (jobs.length === 0) {
		return (
			<motion.div
				initial={{ opacity: 0, scale: 0.95 }}
				animate={{ opacity: 1, scale: 1 }}
				transition={{ duration: 0.5 }}
				className="text-center py-16"
			>
				<div className="mx-auto w-24 h-24 rounded-full bg-muted/50 flex items-center justify-center mb-6">
					<FileText className="h-12 w-12 text-muted-foreground" />
				</div>
				<h3 className="text-xl font-semibold mb-2">No jobs yet</h3>
				<p className="text-muted-foreground mb-6 max-w-md mx-auto">
					Start your first literature review by creating a new job from the home page.
				</p>
				<Button asChild>
					<Link to="/">Start Your First Review</Link>
				</Button>
			</motion.div>
		)
	}

	return (
		<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
			{jobs.map((job, index) => (
				<motion.div
					key={job.job_id}
					initial={{ opacity: 0, y: 20 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: index * 0.1, duration: 0.5 }}
					whileHover={{ y: -4, transition: { duration: 0.2 } }}
				>
					<Card className="h-full hover:shadow-lg transition-all duration-200 border-0 bg-card/50 backdrop-blur-sm">
						<CardHeader className="pb-3">
							<div className="flex items-start justify-between">
								<div className="flex-1 min-w-0">
									<CardTitle className="text-lg font-semibold line-clamp-2 mb-2">
										{job.topic}
									</CardTitle>
									<CardDescription className="flex items-center gap-2 text-sm">
										<Calendar className="h-3 w-3" />
										{formatDate(job.created_at)}
									</CardDescription>
								</div>
								<Badge 
									variant={getStatusVariant(job.status)}
									className="flex items-center gap-1 text-xs"
								>
									{getStatusIcon(job.status)}
									{job.status}
								</Badge>
							</div>
						</CardHeader>
						
						<CardContent className="pt-0">
							<div className="flex items-center justify-between">
								<div className="text-sm text-muted-foreground">
									Job ID: {job.job_id.slice(0, 8)}...
								</div>
								<Button 
									variant="outline" 
									size="sm" 
									asChild
									className="hover:bg-primary hover:text-primary-foreground transition-colors"
								>
									<Link to={`/report/${job.job_id}`} className="flex items-center gap-1">
										<ExternalLink className="h-3 w-3" />
										View
									</Link>
								</Button>
							</div>
						</CardContent>
					</Card>
				</motion.div>
			))}
		</div>
	)
}
