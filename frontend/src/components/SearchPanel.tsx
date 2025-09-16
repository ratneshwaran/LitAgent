import { useState, useEffect } from 'react'
import { Input } from './ui/input'
import { Label } from './ui/label'

interface SearchPanelProps {
	className?: string
	onTopicChange?: (topic: string) => void
	onDescriptionChange?: (description: string) => void
	initialTopic?: string
	initialDescription?: string
}

export default function SearchPanel({ 
	className = '', 
	onTopicChange, 
	onDescriptionChange, 
	initialTopic = '', 
	initialDescription = '' 
}: SearchPanelProps) {
	const [query, setQuery] = useState(initialTopic)
	const [description, setDescription] = useState(initialDescription)

	// Update topic when query changes
	useEffect(() => {
		if (onTopicChange) {
			onTopicChange(query)
		}
	}, [query, onTopicChange])

	// Update description when it changes
	useEffect(() => {
		if (onDescriptionChange) {
			onDescriptionChange(description)
		}
	}, [description, onDescriptionChange])

	return (
		<div className={`space-y-4 ${className}`}>
			<div className="space-y-2">
				<Label htmlFor="title-query">Title keywords</Label>
				<Input
					id="title-query"
					placeholder="e.g., machine learning, neural networks"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					className="h-12 text-base"
				/>
			</div>
			<div className="space-y-2">
				<Label htmlFor="description-query">Description (optional)</Label>
				<textarea
					id="description-query"
					placeholder="e.g., applications in healthcare and drug discovery"
					value={description}
					onChange={(e) => setDescription(e.target.value)}
					className="flex w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-vertical"
					rows={4}
				/>
			</div>
		</div>
	)
}
