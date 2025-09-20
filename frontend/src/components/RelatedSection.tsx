import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { truncateText } from '@/lib/utils';

export type RelatedItem = { id: string; title: string; year?: number; venue?: string; url?: string; doi?: string };
export type RelatedInsights = { themes: string[]; gaps: string[]; future_work: string[]; summary: string };
export type RelatedResponse = { related: RelatedItem[]; insights: RelatedInsights };

interface RelatedSectionProps {
  data?: RelatedResponse;
  loading?: boolean;
  error?: string | null;
}

export function RelatedSection({ data, loading = false, error = null }: RelatedSectionProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Sparkles className="w-4 h-4" />
        <span className="font-medium">Related works</span>
        {loading && <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />}
      </div>

      {error && (
        <div className="text-xs text-destructive flex items-center gap-1">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {!loading && !error && !data && (
        <p className="text-xs text-muted-foreground">No related data loaded yet.</p>
      )}

      {data && (
        <>
          {data.insights?.summary && (
            <p className="text-sm text-muted-foreground break-words whitespace-normal">{data.insights.summary}</p>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {data.insights?.themes?.length > 0 && (
              <div>
                <div className="text-xs font-semibold mb-1">Themes</div>
                <div className="flex flex-wrap gap-1">
                  {data.insights.themes.slice(0, 8).map((t, i) => (
                    <Badge key={i} variant="outline" className="text-xs">{t}</Badge>
                  ))}
                </div>
              </div>
            )}
            {data.insights?.gaps?.length > 0 && (
              <div>
                <div className="text-xs font-semibold mb-1">Gaps</div>
                <ul className="list-disc pl-4 text-xs space-y-1 text-muted-foreground">
                  {data.insights.gaps.slice(0, 6).map((g, i) => (
                    <li key={i} className="break-words whitespace-normal">{g}</li>
                  ))}
                </ul>
              </div>
            )}
            {data.insights?.future_work?.length > 0 && (
              <div>
                <div className="text-xs font-semibold mb-1">Future directions</div>
                <ul className="list-disc pl-4 text-xs space-y-1 text-muted-foreground">
                  {data.insights.future_work.slice(0, 6).map((g, i) => (
                    <li key={i} className="break-words whitespace-normal">{g}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <ul className="list-disc pl-6 space-y-1">
            {data.related.map((r) => (
              <li key={r.id} className="text-sm break-words whitespace-normal">
                <a
                  href={r.url || (r.doi ? `https://doi.org/${r.doi}` : '#')}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {truncateText(r.title, 100)}
                </a>
                {r.venue && <span className="text-muted-foreground"> — {r.venue}</span>} {r.year && <span className="text-muted-foreground">({r.year})</span>}
              </li>
            ))}
          </ul>

          {data.related.length === 0 && (
            <p className="text-xs text-muted-foreground">No related papers found.</p>
          )}
        </>
      )}
    </div>
  );
}

export default RelatedSection;


