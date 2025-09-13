import { motion } from 'framer-motion'
import JobList from '../components/JobList'
import { FileText, Clock } from 'lucide-react'

export default function Jobs(){
	return (
		<div className="min-h-screen py-8">
			<motion.div 
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ duration: 0.6 }}
				className="container mx-auto px-4"
			>
				{/* Header */}
				<div className="text-center mb-12">
					<motion.div
						initial={{ scale: 0.8, opacity: 0 }}
						animate={{ scale: 1, opacity: 1 }}
						transition={{ delay: 0.2, duration: 0.5 }}
						className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4"
					>
						<FileText className="h-4 w-4" />
						Literature Review Jobs
					</motion.div>
					
					<motion.h1 
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.3, duration: 0.6 }}
						className="text-3xl md:text-4xl font-bold tracking-tight mb-4"
					>
						Your Research History
					</motion.h1>
					
					<motion.p 
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.4, duration: 0.6 }}
						className="text-lg text-muted-foreground max-w-2xl mx-auto"
					>
						Track and manage your literature review jobs. View completed reports and monitor running processes.
					</motion.p>
				</div>

				{/* Jobs List */}
				<motion.div
					initial={{ opacity: 0, y: 40 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 0.5, duration: 0.6 }}
				>
					<JobList />
				</motion.div>
			</motion.div>
		</div>
	)
}
