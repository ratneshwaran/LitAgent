import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Paper } from '@/lib/types';
import { 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle, 
  AlertTriangle,
  Lock,
  Code,
  Database,
  FileText,
  Users,
  Calendar,
  Globe,
  BookOpen,
  Sparkles
} from 'lucide-react';
import { truncateText } from '@/lib/utils';

interface PapersTableProps {
  papers: Paper[];
}

export function PapersTable({ papers }: PapersTableProps) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  // Default sort by relevance if available, fallback to year
  const [sortField, setSortField] = useState<keyof Paper>('title' as any);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [related, setRelated] = useState<Record<string, Array<{id:string,title:string,year?:number,venue?:string,url?:string,doi?:string}>>>({});
  const [loadingRelated, setLoadingRelated] = useState<Record<string, boolean>>({});

  const handleSort = (field: keyof Paper) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Preserve backend ranking order when no explicit sortable field is selected.
  const papersWithIndex = papers.map((p, idx) => ({ p, idx }));
  const sortedPapers = papersWithIndex.sort((A, B) => {
    const a = A.p; const b = B.p;
    const aVal = (a as any)[sortField];
    const bVal = (b as any)[sortField];
    
    if (aVal === undefined && bVal === undefined) return 0;
    if (aVal === undefined) return 1;
    if (bVal === undefined) return -1;
    
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortDirection === 'asc' 
        ? aVal.localeCompare(bVal)
        : bVal.localeCompare(aVal);
    }
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    }
    
    // If incomparable, preserve original backend order
    return A.idx - B.idx;
  }).map(({p}) => p);

  const fetchRelated = async (paperId: string) => {
    if (related[paperId]) return; // cached
    setLoadingRelated(prev => ({...prev, [paperId]: true}));
    try {
      const base = (import.meta.env.VITE_BACKEND_URL || '') + '/api/related';
      const resp = await fetch(base, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ paper_id: paperId, k: 10 }) });
      const data = await resp.json();
      setRelated(prev => ({...prev, [paperId]: data}));
    } catch {
      setRelated(prev => ({...prev, [paperId]: []}));
    } finally {
      setLoadingRelated(prev => ({...prev, [paperId]: false}));
    }
  }

  const getFlagIcon = (flag: string) => {
    switch (flag) {
      case 'overclaiming':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'weak_baselines':
        return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      case 'no_data':
        return <Database className="w-4 h-4 text-red-500" />;
      case 'no_code':
        return <Code className="w-4 h-4 text-red-500" />;
      case 'small_sample':
        return <Users className="w-4 h-4 text-yellow-500" />;
      case 'retraction':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'replication_failure':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'legal_primary_source_only':
        return <FileText className="w-4 h-4 text-blue-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-500" />;
    }
  };

  const getFlagLabel = (flag: string) => {
    switch (flag) {
      case 'overclaiming': return 'Overclaiming';
      case 'weak_baselines': return 'Weak baselines';
      case 'no_data': return 'No data';
      case 'no_code': return 'No code';
      case 'small_sample': return 'Small sample';
      case 'retraction': return 'Retraction';
      case 'replication_failure': return 'Replication failure';
      case 'legal_primary_source_only': return 'Primary source only';
      default: return flag;
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">Research Papers</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th 
                  className="text-left p-2 cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort('title')}
                >
                  <div className="flex items-center gap-1">
                    Paper
                    {sortField === 'title' && (
                      sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="text-left p-2 cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort('venue')}
                >
                  <div className="flex items-center gap-1">
                    Venue
                    {sortField === 'venue' && (
                      sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th 
                  className="text-left p-2 cursor-pointer hover:bg-muted/50"
                  onClick={() => handleSort('year')}
                >
                  <div className="flex items-center gap-1">
                    Year
                    {sortField === 'year' && (
                      sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />
                    )}
                  </div>
                </th>
                <th className="text-left p-2">Discipline</th>
                <th className="text-left p-2">Study Type</th>
                <th className="text-left p-2">Key Findings</th>
                <th className="text-left p-2">Flags</th>
                <th className="text-left p-2">Access</th>
                <th className="text-left p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedPapers.map((paper) => (
                <React.Fragment key={paper.id}>
                  <tr className="border-b hover:bg-muted/50">
                    <td className="p-2">
                      <div className="space-y-1">
                        <div className="flex items-start gap-2">
                          <a
                            href={paper.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium line-clamp-2"
                          >
                            {truncateText(paper.title, 80)}
                          </a>
                          <ExternalLink className="w-3 h-3 text-muted-foreground flex-shrink-0 mt-1" />
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {paper.authors.slice(0, 3).join(', ')}
                          {paper.authors.length > 3 && ` et al.`}
                        </div>
                      </div>
                    </td>
                    <td className="p-2">
                      {paper.venue && (
                        <Badge variant="outline" className="text-xs">
                          {truncateText(paper.venue, 20)}
                        </Badge>
                      )}
                    </td>
                    <td className="p-2">
                      {paper.year && (
                        <div className="flex items-center gap-1 text-sm">
                          <Calendar className="w-3 h-3" />
                          {paper.year}
                        </div>
                      )}
                    </td>
                    <td className="p-2">
                      {paper.discipline && (
                        <Badge variant="secondary" className="text-xs">
                          {paper.discipline}
                        </Badge>
                      )}
                    </td>
                    <td className="p-2">
                      {paper.studyType && (
                        <Badge variant="outline" className="text-xs">
                          {paper.studyType}
                        </Badge>
                      )}
                    </td>
                    <td className="p-2">
                      {paper.keyFindings && (
                        <div className="text-sm text-muted-foreground max-w-xs">
                          {truncateText(paper.keyFindings, 60)}
                        </div>
                      )}
                    </td>
                    <td className="p-2">
                      {paper.flags && paper.flags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {paper.flags.slice(0, 2).map((flag, index) => (
                            <div key={index} className="flex items-center gap-1" title={getFlagLabel(flag)}>
                              {getFlagIcon(flag)}
                            </div>
                          ))}
                          {paper.flags.length > 2 && (
                            <span className="text-xs text-muted-foreground">
                              +{paper.flags.length - 2}
                            </span>
                          )}
                        </div>
                      )}
                    </td>
                    <td className="p-2">
                      <div className="flex items-center gap-1">
                        {paper.peerReviewed && (
                          <div title="Peer-reviewed">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          </div>
                        )}
                        {paper.openAccess && (
                          <div title="Open access">
                            <Globe className="w-4 h-4 text-blue-500" />
                          </div>
                        )}
                        {paper.preregistered && (
                          <div title="Preregistered">
                            <FileText className="w-4 h-4 text-purple-500" />
                          </div>
                        )}
                        {paper.dataUrl && (
                          <div title="Data available">
                            <Database className="w-4 h-4 text-green-500" />
                          </div>
                        )}
                        {paper.codeUrl && (
                          <div title="Code available">
                            <Code className="w-4 h-4 text-green-500" />
                          </div>
                        )}
                        {paper.ethicsApproval && (
                          <div title="Ethics approved">
                            <Lock className="w-4 h-4 text-blue-500" />
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="p-2">
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={() => fetchRelated(paper.id)} disabled={!!loadingRelated[paper.id]}>
                          <Sparkles className="w-4 h-4 mr-1" /> More like this
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => {
                          const next = new Set(expandedRows);
                          next.has(paper.id) ? next.delete(paper.id) : next.add(paper.id);
                          setExpandedRows(next);
                        }}>
                          {expandedRows.has(paper.id) ? <><ChevronUp className="w-4 h-4 mr-1" />Collapse</> : <><ChevronDown className="w-4 h-4 mr-1" />Expand</>}
                        </Button>
                      </div>
                    </td>
                  </tr>
                  {expandedRows.has(paper.id) && (
                    <tr className="border-b bg-muted/20">
                      <td colSpan={9} className="p-4">
                        <div className="space-y-4">
                          {/* Abstract */}
                          {paper.abstract && (
                            <div>
                              <h4 className="font-medium mb-2 flex items-center gap-2">
                                <BookOpen className="w-4 h-4" />
                                Abstract
                              </h4>
                              <p className="text-sm text-muted-foreground leading-relaxed">
                                {paper.abstract}
                              </p>
                            </div>
                          )}

                          {/* Additional Details */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {paper.population && (
                              <div>
                                <h4 className="font-medium mb-1">Population</h4>
                                <p className="text-sm text-muted-foreground">{paper.population}</p>
                              </div>
                            )}
                            {paper.sampleSize && (
                              <div>
                                <h4 className="font-medium mb-1">Sample Size</h4>
                                <p className="text-sm text-muted-foreground">{paper.sampleSize}</p>
                              </div>
                            )}
                            {paper.geography && (
                              <div>
                                <h4 className="font-medium mb-1">Geography</h4>
                                <p className="text-sm text-muted-foreground">{paper.geography}</p>
                              </div>
                            )}
                            {paper.languages && paper.languages.length > 0 && (
                              <div>
                                <h4 className="font-medium mb-1">Languages</h4>
                                <div className="flex flex-wrap gap-1">
                                  {paper.languages.map((lang, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {lang}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Links */}
                          <div className="flex flex-wrap gap-2">
                            {paper.dataUrl && (
                              <Button variant="outline" size="sm" asChild>
                                <a href={paper.dataUrl} target="_blank" rel="noopener noreferrer">
                                  <Database className="w-4 h-4 mr-2" />
                                  Data
                                </a>
                              </Button>
                            )}
                            {paper.codeUrl && (
                              <Button variant="outline" size="sm" asChild>
                                <a href={paper.codeUrl} target="_blank" rel="noopener noreferrer">
                                  <Code className="w-4 h-4 mr-2" />
                                  Code
                                </a>
                              </Button>
                            )}
                            {paper.doi && (
                              <Button variant="outline" size="sm" asChild>
                                <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener noreferrer">
                                  <ExternalLink className="w-4 h-4 mr-2" />
                                  DOI
                                </a>
                              </Button>
                            )}
                          </div>

                          {/* Related */}
                          {related[paper.id] && (
                            <div>
                              <h4 className="font-medium mb-2 flex items-center gap-2">
                                <Sparkles className="w-4 h-4" /> Related works
                              </h4>
                              <ul className="list-disc pl-6 space-y-1">
                                {related[paper.id]!.map((r) => (
                                  <li key={r.id} className="text-sm">
                                    <a href={r.url || (r.doi ? `https://doi.org/${r.doi}` : '#')} target="_blank" className="text-blue-600 hover:underline">
                                      {truncateText(r.title, 100)}
                                    </a>
                                    {r.venue && <span className="text-muted-foreground"> — {r.venue}</span>} {r.year && <span className="text-muted-foreground">({r.year})</span>}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Expand/Collapse All */}
        <div className="flex justify-center mt-4">
          <Button
            variant="outline"
            onClick={() => {
              if (expandedRows.size === papers.length) {
                setExpandedRows(new Set());
              } else {
                setExpandedRows(new Set(papers.map(p => p.id)));
              }
            }}
          >
            {expandedRows.size === papers.length ? (
              <>
                <ChevronUp className="w-4 h-4 mr-2" />
                Collapse All
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4 mr-2" />
                Expand All
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
