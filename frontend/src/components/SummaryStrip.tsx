import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SearchSummary } from '@/lib/types';
import { formatDate } from '@/lib/utils';
import { Calendar, Database, Globe, Clock } from 'lucide-react';

interface SummaryStripProps {
  summary: SearchSummary;
}

export function SummaryStrip({ summary }: SummaryStripProps) {
  const { total, disciplines, sources, yearSpan, generatedAt } = summary;

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="flex flex-wrap items-center gap-4 text-sm">
          {/* Total Results */}
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-muted-foreground" />
            <span className="font-medium">{total.toLocaleString()}</span>
            <span className="text-muted-foreground">results</span>
          </div>

          {/* Year Span */}
          {yearSpan && (
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">
                {yearSpan[0]} - {yearSpan[1]}
              </span>
            </div>
          )}

          {/* Disciplines */}
          {disciplines.length > 0 && (
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-muted-foreground" />
              <div className="flex flex-wrap gap-1">
                {disciplines.slice(0, 3).map((discipline) => (
                  <Badge key={discipline} variant="outline" className="text-xs">
                    {discipline}
                  </Badge>
                ))}
                {disciplines.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{disciplines.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Sources */}
          {sources.length > 0 && (
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-muted-foreground" />
              <div className="flex flex-wrap gap-1">
                {sources.slice(0, 3).map((source) => (
                  <Badge key={source} variant="secondary" className="text-xs">
                    {source}
                  </Badge>
                ))}
                {sources.length > 3 && (
                  <Badge variant="secondary" className="text-xs">
                    +{sources.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Generated At */}
          <div className="flex items-center gap-2 ml-auto">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              {formatDate(generatedAt)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
