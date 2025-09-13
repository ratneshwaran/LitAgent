import { Link, NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Moon, Sun, Github, BookOpen } from 'lucide-react'
import { Button } from './ui/button'

export default function Navbar() {
	const [dark, setDark] = useState<boolean>(() => window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
	
	useEffect(() => {
		document.documentElement.classList.toggle('dark', dark)
	}, [dark])

	return (
		<motion.header 
			initial={{ y: -100, opacity: 0 }}
			animate={{ y: 0, opacity: 1 }}
			transition={{ duration: 0.5 }}
			className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
		>
			<div className="container mx-auto px-4 py-4 flex items-center justify-between">
				<Link to="/" className="flex items-center space-x-2 group">
					<div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
						<BookOpen className="h-5 w-5 text-primary" />
					</div>
					<span className="text-xl font-bold bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
						LitRev
					</span>
				</Link>
				
				<nav className="flex items-center gap-6">
					<NavLink 
						to="/" 
						className={({ isActive }) => 
							`text-sm font-medium transition-colors hover:text-primary ${
								isActive ? 'text-primary' : 'text-muted-foreground'
							}`
						}
					>
						Home
					</NavLink>
					<NavLink 
						to="/jobs" 
						className={({ isActive }) => 
							`text-sm font-medium transition-colors hover:text-primary ${
								isActive ? 'text-primary' : 'text-muted-foreground'
							}`
						}
					>
						Jobs
					</NavLink>
					
					<div className="flex items-center gap-2">
						<Button
							variant="ghost"
							size="icon"
							onClick={() => setDark(v => !v)}
							className="h-9 w-9"
						>
							{dark ? (
								<Sun className="h-4 w-4" />
							) : (
								<Moon className="h-4 w-4" />
							)}
							<span className="sr-only">Toggle theme</span>
						</Button>
						
						<Button
							variant="ghost"
							size="icon"
							asChild
							className="h-9 w-9"
						>
							<a 
								href="https://github.com/your-repo/literature-review-agent" 
								target="_blank" 
								rel="noopener noreferrer"
							>
								<Github className="h-4 w-4" />
								<span className="sr-only">GitHub</span>
							</a>
						</Button>
					</div>
				</nav>
			</div>
		</motion.header>
	)
}
