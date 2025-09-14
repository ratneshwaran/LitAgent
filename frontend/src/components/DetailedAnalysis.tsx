import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChevronDown, ChevronRight, ExternalLink, AlertTriangle, Lock, BarChart3, TrendingUp, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Button } from './ui/button'

interface CritiqueFlag {
  tag: string
  severity: string
  icon: string
  rationale?: string
}

interface Quote {
  text: string
  section?: string
}

interface PaperDetail {
  id: string
  title: string
  title_link?: string
  venue?: string
  year?: number
  authors?: string[]
  tldr?: string
  methods?: string[]
  results?: string[]
  limitations?: string[]
  critique_flags?: CritiqueFlag[]
  quotes?: Quote[]
}

interface DetailedAnalysisProps {
  data: {
    comparative: any[]
    detailed: PaperDetail[]
    key_insights: {
      gaps: string[]
      future_work: string[]
    }
  }
}

export default function DetailedAnalysis({ data }: DetailedAnalysisProps) {
  const [expandedPapers, setExpandedPapers] = useState<Set<string>>(new Set())

  const togglePaper = (paperId: string) => {
    const newExpanded = new Set(expandedPapers)
    if (newExpanded.has(paperId)) {
      newExpanded.delete(paperId)
    } else {
      newExpanded.add(paperId)
    }
    setExpandedPapers(newExpanded)
  }

  const getCritiqueIcon = (tag: string) => {
    const tagLower = tag.toLowerCase()
    if (tagLower.includes('baseline')) return <AlertTriangle className="h-4 w-4" />
    if (tagLower.includes('reproducibility')) return <Lock className="h-4 w-4" />
    if (tagLower.includes('data')) return <BarChart3 className="h-4 w-4" />
    if (tagLower.includes('evaluation')) return <TrendingUp className="h-4 w-4" />
    return <AlertTriangle className="h-4 w-4" />
  }

  const getSeverityColor = (severity: string) => {
    const severityLower = severity.toLowerCase()
    if (severityLower.includes('high')) return 'destructive'
    if (severityLower.includes('medium') || severityLower.includes('med')) return 'default'
    return 'secondary'
  }

  return (
    <div className="space-y-6">
      {/* Key Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            🔍 Key Insights
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.key_insights.gaps.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                🔍 Identified Gaps
              </h4>
              <ul className="space-y-1">
                {data.key_insights.gaps.map((gap, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-muted-foreground">•</span>
                    <span>{gap}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {data.key_insights.future_work.length > 0 && (
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                🚀 Future Research Directions
              </h4>
              <ul className="space-y-1">
                {data.key_insights.future_work.map((future, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-muted-foreground">•</span>
                    <span>{future}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Comparative Analysis Table */}
      <Card>
        <CardHeader>
          <CardTitle>📊 Comparative Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2 font-semibold">Paper</th>
                  <th className="text-left p-2 font-semibold">Venue</th>
                  <th className="text-left p-2 font-semibold">Year</th>
                  <th className="text-left p-2 font-semibold">Methods</th>
                  <th className="text-left p-2 font-semibold">Results</th>
                  <th className="text-left p-2 font-semibold">Flags</th>
                </tr>
              </thead>
              <tbody>
                {data.comparative.map((paper, index) => (
                  <tr key={paper.id} className="border-b hover:bg-muted/50">
                    <td className="p-2">
                      <div className="max-w-xs">
                        {paper.title_link ? (
                          <a 
                            href={paper.title_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 underline flex items-center gap-1"
                          >
                            {paper.title.length > 50 ? `${paper.title.substring(0, 47)}...` : paper.title}
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : (
                          <span className="text-foreground">
                            {paper.title.length > 50 ? `${paper.title.substring(0, 47)}...` : paper.title}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="p-2 text-sm text-muted-foreground">
                      {paper.venue || 'Unknown'}
                    </td>
                    <td className="p-2 text-sm text-muted-foreground">
                      {paper.year || 'N/A'}
                    </td>
                    <td className="p-2 text-sm">
                      <div className="max-w-xs">
                        {paper.methods && paper.methods.length > 50 
                          ? `${paper.methods.substring(0, 47)}...` 
                          : paper.methods || 'Not specified'
                        }
                      </div>
                    </td>
                    <td className="p-2 text-sm">
                      <div className="max-w-xs">
                        {paper.results && paper.results.length > 50 
                          ? `${paper.results.substring(0, 47)}...` 
                          : paper.results || 'Not specified'
                        }
                      </div>
                    </td>
                    <td className="p-2">
                      <div className="flex flex-wrap gap-1">
                        {paper.critique_flags && paper.critique_flags.length > 0 ? (
                          paper.critique_flags.slice(0, 2).map((flag, flagIndex) => (
                            <Badge key={flagIndex} variant="outline" className="text-xs">
                              {flag.icon} {flag.tag}
                            </Badge>
                          ))
                        ) : (
                          <Badge variant="secondary" className="text-xs">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            No major issues
                          </Badge>
                        )}
                        {paper.critique_flags && paper.critique_flags.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{paper.critique_flags.length - 2} more
                          </Badge>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Paper Reviews */}
      <Card>
        <CardHeader>
          <CardTitle>📚 Detailed Paper Reviews</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.detailed.map((paper, index) => (
            <motion.div
              key={paper.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="border-l-4 border-l-blue-500">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">
                        {index + 1}. {paper.title_link ? (
                          <a 
                            href={paper.title_link} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 underline flex items-center gap-1"
                          >
                            {paper.title}
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        ) : (
                          paper.title
                        )}
                      </CardTitle>
                      
                      <div className="flex flex-wrap gap-2 text-sm text-muted-foreground mb-3">
                        {paper.venue && <span>Venue: {paper.venue}</span>}
                        {paper.year && <span>Year: {paper.year}</span>}
                        {paper.authors && paper.authors.length > 0 && (
                          <span>Authors: {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}</span>
                        )}
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => togglePaper(paper.id)}
                      className="ml-4"
                    >
                      {expandedPapers.has(paper.id) ? (
                        <ChevronDown className="h-4 w-4" />
                      ) : (
                        <ChevronRight className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </CardHeader>
                
                {expandedPapers.has(paper.id) && (
                  <CardContent className="pt-0 space-y-4">
                    {/* TL;DR */}
                    {paper.tldr && (
                      <div>
                        <h4 className="font-semibold mb-2">TL;DR</h4>
                        <p className="text-sm text-muted-foreground">{paper.tldr}</p>
                      </div>
                    )}
                    
                    {/* Methods */}
                    {paper.methods && paper.methods.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Methods</h4>
                        <ul className="space-y-1">
                          {paper.methods.map((method, methodIndex) => (
                            <li key={methodIndex} className="flex items-start gap-2 text-sm">
                              <span className="text-muted-foreground">•</span>
                              <span>{method}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Results */}
                    {paper.results && paper.results.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Results</h4>
                        <ul className="space-y-1">
                          {paper.results.map((result, resultIndex) => (
                            <li key={resultIndex} className="flex items-start gap-2 text-sm">
                              <span className="text-muted-foreground">•</span>
                              <span>{result}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Limitations */}
                    {paper.limitations && paper.limitations.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Limitations</h4>
                        <ul className="space-y-1">
                          {paper.limitations.map((limitation, limitationIndex) => (
                            <li key={limitationIndex} className="flex items-start gap-2 text-sm">
                              <span className="text-muted-foreground">•</span>
                              <span>{limitation}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {/* Critique Flags */}
                    {paper.critique_flags && paper.critique_flags.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Critique Flags</h4>
                        <div className="space-y-2">
                          {paper.critique_flags.map((flag, flagIndex) => (
                            <div key={flagIndex} className="flex items-start gap-2">
                              <Badge variant={getSeverityColor(flag.severity)} className="text-xs">
                                {getCritiqueIcon(flag.tag)}
                                <span className="ml-1">{flag.tag}</span>
                              </Badge>
                              <span className="text-sm text-muted-foreground">{flag.rationale}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Key Quotes */}
                    {paper.quotes && paper.quotes.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Key Quotes</h4>
                        <div className="space-y-3">
                          {paper.quotes.map((quote, quoteIndex) => (
                            <blockquote key={quoteIndex} className="border-l-4 border-blue-200 pl-4 italic text-sm">
                              "{quote.text}"
                              {quote.section && (
                                <cite className="block mt-1 text-xs text-muted-foreground not-italic">
                                  — {quote.section}
                                </cite>
                              )}
                            </blockquote>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            </motion.div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
