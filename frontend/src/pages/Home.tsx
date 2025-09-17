import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Header } from '@/components/Header';
import { SearchBox } from '@/components/SearchBox';
import { AdvancedFilters } from '@/components/AdvancedFilters';
import { SummaryStrip } from '@/components/SummaryStrip';
import { KeyInsights } from '@/components/KeyInsights';
import { PapersTable } from '@/components/PapersTable';
import { RefineChat } from '@/components/RefineChat';
import { ExportMenu } from '@/components/ExportMenu';
import { useUIStore } from '@/lib/store';
import { parseQuery, mergeQueryWithFilters } from '@/lib/query-parser';
import { searchLiterature } from '@/lib/api';
import { ParsedQuery } from '@/lib/types';
import { Loader2, AlertCircle } from 'lucide-react';

export function Home() {
  const [darkMode, setDarkMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState<ParsedQuery | null>(null);
  const [searchNonce, setSearchNonce] = useState(0);
  const { filters } = useUIStore();

  const { data: searchResults, isLoading, error, refetch, dataUpdatedAt } = useQuery({
    queryKey: ['search', searchQuery, searchNonce],
    queryFn: () => searchLiterature(searchQuery!),
    enabled: !!searchQuery,
    staleTime: 0,
    refetchOnMount: 'always',
    refetchOnReconnect: 'always',
    refetchOnWindowFocus: false,
  });

  const handleSearch = (query: string) => {
    const parsedQuery = parseQuery(query);
    const mergedQuery = mergeQueryWithFilters(parsedQuery, filters);
    setSearchQuery(mergedQuery);
    setSearchNonce((n) => n + 1);
  };

  const handleRefine = (refinedQuery: ParsedQuery) => {
    // Client-side refine: if we have current results, filter/rerank on the fly to avoid flicker
    if (searchResults && Array.isArray(searchResults.papers)) {
      // Store refined query so a background refetch can update later
      setSearchQuery(refinedQuery);
      // Trigger a background refetch without toggling loading UI
      refetch({ cancelRefetch: false });
    } else {
      setSearchQuery(refinedQuery);
      setSearchNonce((n) => n + 1);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    // TODO: Implement actual theme switching
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark' : ''}`}>
      <Header darkMode={darkMode} onToggleDarkMode={toggleDarkMode} />
      
      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Search Section */}
        <div className="space-y-6">
          <div className="text-center space-y-2">
            <h2 className="text-3xl font-bold">Search Academic Literature</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Ask LitAgent in plain English to find and analyze research papers across all academic fields. 
              Use natural language queries or advanced filters to discover the latest research.
            </p>
          </div>

          <SearchBox onSearch={handleSearch} loading={isLoading} />
          <AdvancedFilters />
        </div>

        {/* Results Section */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-4">
              <Loader2 className="w-8 h-8 animate-spin mx-auto" />
              <p className="text-muted-foreground">Searching literature...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center space-y-4">
              <AlertCircle className="w-8 h-8 text-destructive mx-auto" />
              <div>
                <p className="text-destructive font-medium">Search failed</p>
                <p className="text-muted-foreground text-sm">
                  {error instanceof Error ? error.message : 'An unexpected error occurred'}
                </p>
                <button
                  onClick={() => refetch()}
                  className="mt-2 text-sm text-primary hover:underline"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        )}

        {searchResults && (
          <div className="space-y-6">
            {/* Summary Strip */}
            <SummaryStrip summary={searchResults.summary} />

            {/* Key Insights */}
            <KeyInsights summary={searchResults.summary} />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Papers Table - Takes up 3 columns */}
              <div className="lg:col-span-3">
                <PapersTable papers={searchResults.papers} />
              </div>

              {/* Sidebar - Takes up 1 column */}
              <div className="space-y-6">
                <RefineChat onRefine={handleRefine} loading={isLoading} />
                <ExportMenu query={searchQuery!} results={searchResults} />
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!searchResults && !isLoading && !error && (
          <div className="text-center py-12">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Ready to search?</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Enter your research question in the search box above. 
                Try queries like "machine learning in healthcare" or "climate change economics since 2020".
              </p>
              <div className="flex flex-wrap justify-center gap-2 mt-6">
                {[
                  "Find RCTs on intermittent fasting",
                  "Roman law property rights",
                  "AI bias in hiring decisions",
                  "Climate change adaptation strategies"
                ].map((example) => (
                  <button
                    key={example}
                    onClick={() => handleSearch(example)}
                    className="px-3 py-1 text-sm bg-muted hover:bg-muted/80 rounded-full transition-colors"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}