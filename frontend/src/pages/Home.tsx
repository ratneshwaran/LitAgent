import { motion } from 'framer-motion'
import JobForm from '../components/JobForm'
import { Sparkles, Search, FileText, Brain } from 'lucide-react'

export default function Home(){
	return (
		<div className="min-h-screen">
			{/* Hero Section */}
			<motion.div 
				initial={{ opacity: 0, y: 20 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ duration: 0.6 }}
				className="relative overflow-hidden bg-gradient-to-br from-background via-background to-primary/5 py-20"
			>
				{/* Background Pattern */}
				<div className="absolute inset-0 bg-grid-pattern opacity-5" />
				
				<div className="container mx-auto px-4 text-center">
					<motion.div
						initial={{ scale: 0.8, opacity: 0 }}
						animate={{ scale: 1, opacity: 1 }}
						transition={{ delay: 0.2, duration: 0.5 }}
						className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6"
					>
						<Sparkles className="h-4 w-4" />
						AI-Powered Literature Review Assistant
					</motion.div>
					
					<motion.h1 
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.3, duration: 0.6 }}
						className="text-4xl md:text-6xl font-bold tracking-tight mb-6"
					>
						Transform Research with{' '}
						<span className="bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
							AI Intelligence
						</span>
					</motion.h1>
					
					<motion.p 
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.4, duration: 0.6 }}
						className="text-xl text-muted-foreground max-w-2xl mx-auto mb-12"
					>
						Search, summarize, critique, and synthesize academic papers into comprehensive, 
						structured literature reviews powered by advanced AI.
					</motion.p>
					
					{/* Feature Icons */}
					<motion.div 
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.5, duration: 0.6 }}
						className="flex justify-center gap-8 mb-16"
					>
						<div className="flex flex-col items-center gap-2">
							<div className="p-3 rounded-lg bg-primary/10">
								<Search className="h-6 w-6 text-primary" />
							</div>
							<span className="text-sm font-medium">Smart Search</span>
						</div>
						<div className="flex flex-col items-center gap-2">
							<div className="p-3 rounded-lg bg-primary/10">
								<Brain className="h-6 w-6 text-primary" />
							</div>
							<span className="text-sm font-medium">AI Analysis</span>
						</div>
						<div className="flex flex-col items-center gap-2">
							<div className="p-3 rounded-lg bg-primary/10">
								<FileText className="h-6 w-6 text-primary" />
							</div>
							<span className="text-sm font-medium">Structured Reports</span>
						</div>
					</motion.div>
				</div>
			</motion.div>
			
			{/* Form Section */}
			<motion.div 
				initial={{ opacity: 0, y: 40 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ delay: 0.6, duration: 0.6 }}
				className="container mx-auto px-4 -mt-10 relative z-10"
			>
				<JobForm />
			</motion.div>
		</div>
	)
}
