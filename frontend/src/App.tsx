import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Jobs from './pages/Jobs'
import Report from './pages/Report'

export default function App() {
	return (
		<div className="min-h-screen bg-background text-foreground">
			<Navbar />
			<Routes>
				<Route path="/" element={<Home />} />
				<Route path="/jobs" element={<Jobs />} />
				<Route path="/report/:jobId" element={<Report />} />
			</Routes>
		</div>
	)
}
