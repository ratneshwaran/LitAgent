import React, { useState } from 'react';
import { Search, Settings, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { useUIStore } from '@/lib/store';

interface SearchBoxProps {
  onSearch: (query: string) => void;
  loading?: boolean;
}

export function SearchBox({ onSearch, loading = false }: SearchBoxProps) {
  const { nl, advancedOpen, toggleAdvanced } = useUIStore();
  const [localNL, setLocalNL] = useState(nl || '');

  const handleSearch = () => {
    const trimmedQuery = localNL.trim();
    if (trimmedQuery) {
      onSearch(trimmedQuery);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Main Search Card */}
      <div className="bg-card border rounded-lg p-6 shadow-sm">
        <div className="space-y-4">
          {/* Search Input */}
          <div className="space-y-2">
            <Textarea
              value={localNL}
              onChange={(e) => setLocalNL(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask in plain English… e.g., 'Find randomized trials on intermittent fasting since 2018; exclude animals; prioritize JAMA/NEJM.' or 'Early Roman law on property rights; Latin sources; translations since 2000.'"
              className="min-h-[120px] text-base resize-none"
              disabled={loading}
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button 
                onClick={handleSearch} 
                disabled={loading || !localNL.trim()}
                className="px-6"
              >
                <Search className="w-4 h-4 mr-2" />
                {loading ? 'Searching...' : 'Search'}
              </Button>
              
              <Button
                variant="outline"
                onClick={toggleAdvanced}
                className="px-4"
              >
                <Settings className="w-4 h-4 mr-2" />
                Advanced filters
                {advancedOpen ? (
                  <ChevronUp className="w-4 h-4 ml-2" />
                ) : (
                  <ChevronDown className="w-4 h-4 ml-2" />
                )}
              </Button>
            </div>

            <div className="text-sm text-muted-foreground">
              Press <kbd className="px-2 py-1 bg-muted rounded text-xs">⌘</kbd> + <kbd className="px-2 py-1 bg-muted rounded text-xs">Enter</kbd> to search
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
