import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useUIStore } from '@/lib/store';
import { parseQuery, mergeQueryWithFilters } from '@/lib/query-parser';
import { ParsedQuery } from '@/lib/types';
import { Send, X, MessageSquare } from 'lucide-react';

interface RefineChatProps {
  onRefine: (query: ParsedQuery) => void;
  loading?: boolean;
}

export function RefineChat({ onRefine, loading = false }: RefineChatProps) {
  const { filters, setNL, setFilters } = useUIStore();
  const [refinement, setRefinement] = useState('');
  const [activeFilters, setActiveFilters] = useState<Record<string, any>>({});
  const [qa, setQa] = useState('');
  const [qaAnswer, setQaAnswer] = useState<string>('');
  const [qaLoading, setQaLoading] = useState(false);

  const handleRefine = () => {
    if (!refinement.trim()) return;

    // Parse the refinement query
    const parsedRefinement = parseQuery(refinement);
    
    // Merge with existing filters
    const mergedQuery = mergeQueryWithFilters(parsedRefinement, filters);
    
    // Update the main query
    setNL(refinement);
    setFilters(mergedQuery);
    
    // Trigger search
    onRefine(mergedQuery);
    
    // Clear refinement input
    setRefinement('');
    
    // Update active filters display
    setActiveFilters(mergedQuery);
  };

  const removeFilter = (key: string, value?: string) => {
    const newFilters = { ...filters };
    
    if (value && Array.isArray(newFilters[key as keyof typeof newFilters])) {
      const array = newFilters[key as keyof typeof newFilters] as string[];
      (newFilters[key as keyof typeof newFilters] as string[]) = array.filter(item => item !== value);
    } else {
      delete newFilters[key as keyof typeof newFilters];
    }
    
    setFilters(newFilters);
    setActiveFilters(newFilters);
  };

  const clearAllFilters = () => {
    setFilters({});
    setActiveFilters({});
  };

  const getFilterDisplayValue = (key: string, value: any): string => {
    if (Array.isArray(value)) {
      return `${key}: ${value.join(', ')}`;
    }
    if (typeof value === 'object' && value !== null) {
      const entries = Object.entries(value).filter(([_, v]) => v === true);
      return entries.length > 0 ? `${key}: ${entries.map(([k]) => k).join(', ')}` : '';
    }
    return `${key}: ${value}`;
  };

  const askQuestion = async () => {
    if (!qa.trim()) return;
    try {
      setQaLoading(true);
      const base = (import.meta.env.VITE_BACKEND_URL || '') + '/api/qa';
      const resp = await fetch(base, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: qa, paper_ids: [filters?.nl || ''] })});
      const data = await resp.json();
      setQaAnswer(data.answer || '');
    } catch (e) {
      setQaAnswer('Unable to answer right now.');
    } finally {
      setQaLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <MessageSquare className="w-5 h-5" />
          Refine Search
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Active Filters */}
        {Object.keys(activeFilters).length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium">Active Filters</h4>
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFilters}
                className="text-xs"
              >
                Clear All
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(activeFilters).map(([key, value]) => {
                if (Array.isArray(value)) {
                  return value.map((item, index) => (
                    <Badge
                      key={`${key}-${index}`}
                      variant="secondary"
                      className="flex items-center gap-1"
                    >
                      {item}
                      <X
                        className="w-3 h-3 cursor-pointer"
                        onClick={() => removeFilter(key, item)}
                      />
                    </Badge>
                  ));
                } else if (typeof value === 'object' && value !== null) {
                  const entries = Object.entries(value).filter(([_, v]) => v === true);
                  return entries.map(([subKey, _]) => (
                    <Badge
                      key={`${key}-${subKey}`}
                      variant="secondary"
                      className="flex items-center gap-1"
                    >
                      {subKey}
                      <X
                        className="w-3 h-3 cursor-pointer"
                        onClick={() => {
                          const newFilters = { ...filters };
                          if (newFilters[key as keyof typeof newFilters]) {
                            (newFilters[key as keyof typeof newFilters] as any)[subKey] = false;
                          }
                          setFilters(newFilters);
                          setActiveFilters(newFilters);
                        }}
                      />
                    </Badge>
                  ));
                } else if (value !== undefined && value !== null && value !== '') {
                  return (
                    <Badge
                      key={key}
                      variant="secondary"
                      className="flex items-center gap-1"
                    >
                      {getFilterDisplayValue(key, value)}
                      <X
                        className="w-3 h-3 cursor-pointer"
                        onClick={() => removeFilter(key)}
                      />
                    </Badge>
                  );
                }
                return null;
              })}
            </div>
          </div>
        )}

        {/* Refinement Input */}
        <div className="space-y-2">
          <div className="flex gap-2">
            <Input
              value={refinement}
              onChange={(e) => setRefinement(e.target.value)}
              placeholder="Refine your search... e.g., 'Only peer-reviewed in medicine since 2019'"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleRefine();
                }
              }}
              disabled={loading}
            />
            <Button
              onClick={handleRefine}
              disabled={loading || !refinement.trim()}
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* QA over results */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Ask about these results</h4>
          <div className="flex gap-2">
            <Input value={qa} onChange={(e)=>setQa(e.target.value)} placeholder="e.g., What methods are used in 2019+ RCTs?" />
            <Button onClick={askQuestion} disabled={qaLoading || !qa.trim()}>Ask</Button>
          </div>
          {qaAnswer && (
            <div className="text-sm text-muted-foreground whitespace-pre-wrap border rounded p-3 bg-muted/30">{qaAnswer}</div>
          )}
        </div>

        {/* Example Refinements */}
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Quick Refinements</h4>
          <div className="flex flex-wrap gap-2">
            {[
              "Only peer-reviewed",
              "Exclude animals",
              "Since 2020",
              "With data available",
              "Meta-analyses only",
              "Open access only"
            ].map((example) => (
              <Button
                key={example}
                variant="outline"
                size="sm"
                onClick={() => setRefinement(example)}
                className="text-xs"
              >
                {example}
              </Button>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
