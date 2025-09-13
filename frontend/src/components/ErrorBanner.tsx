import { motion } from 'framer-motion'
import { AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from './ui/button'

type Props = { 
	message: string
	onRetry?: () => void
}

export default function ErrorBanner({ message, onRetry }: Props) {
	if (!message) return null
	
	return (
		<motion.div
			initial={{ opacity: 0, y: -20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.3 }}
			className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-destructive/5"
		>
			<div className="max-w-md mx-auto text-center space-y-6">
				<motion.div
					initial={{ scale: 0.8, opacity: 0 }}
					animate={{ scale: 1, opacity: 1 }}
					transition={{ delay: 0.2, duration: 0.5 }}
					className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto"
				>
					<AlertCircle className="h-8 w-8 text-destructive" />
				</motion.div>
				
				<div className="space-y-2">
					<motion.h2
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.3 }}
						className="text-xl font-semibold"
					>
						Something went wrong
					</motion.h2>
					<motion.p
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.4 }}
						className="text-muted-foreground"
					>
						{message}
					</motion.p>
				</div>
				
				{onRetry && (
					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.5 }}
					>
						<Button
							onClick={onRetry}
							variant="outline"
							className="flex items-center gap-2"
						>
							<RefreshCw className="h-4 w-4" />
							Try Again
						</Button>
					</motion.div>
				)}
			</div>
		</motion.div>
	)
}
