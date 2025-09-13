import { motion } from 'framer-motion'
import { Loader2, Brain } from 'lucide-react'

export default function Loader() {
	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-primary/5">
			<motion.div
				initial={{ opacity: 0, scale: 0.8 }}
				animate={{ opacity: 1, scale: 1 }}
				transition={{ duration: 0.5 }}
				className="text-center space-y-6"
			>
				<div className="relative">
					<motion.div
						className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full mx-auto"
						animate={{ rotate: 360 }}
						transition={{ repeat: Infinity, ease: 'linear', duration: 1 }}
					/>
					<motion.div
						className="absolute inset-0 flex items-center justify-center"
						animate={{ scale: [1, 1.1, 1] }}
						transition={{ repeat: Infinity, duration: 2 }}
					>
						<Brain className="h-6 w-6 text-primary" />
					</motion.div>
				</div>
				
				<div className="space-y-2">
					<motion.h2
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.2 }}
						className="text-xl font-semibold"
					>
						AI Review in Progress
					</motion.h2>
					<motion.p
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.3 }}
						className="text-muted-foreground"
					>
						Analyzing papers and generating insights...
					</motion.p>
				</div>
			</motion.div>
		</div>
	)
}
