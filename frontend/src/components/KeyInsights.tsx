import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SearchSummary } from '@/lib/types';
import { Lightbulb, Bug, Rocket } from 'lucide-react';

interface KeyInsightsProps {
  summary: SearchSummary;
}

export function KeyInsights({ summary }: KeyInsightsProps) {
  const { keyInsights } = summary;
  const { themes, gaps, futureWork } = keyInsights;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
      {/* Themes */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            Key Themes
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {themes.length > 0 ? (
            themes.map((theme, index) => (
              <Badge key={index} variant="outline" className="block w-fit">
                {theme}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No themes identified</p>
          )}
        </CardContent>
      </Card>

      {/* Gaps */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Bug className="w-5 h-5 text-red-500" />
            Research Gaps
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {gaps.length > 0 ? (
            gaps.map((gap, index) => (
              <Badge key={index} variant="destructive" className="block w-fit">
                {gap}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No gaps identified</p>
          )}
        </CardContent>
      </Card>

      {/* Future Work */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Rocket className="w-5 h-5 text-blue-500" />
            Future Directions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {futureWork.length > 0 ? (
            futureWork.map((work, index) => (
              <Badge key={index} variant="secondary" className="block w-fit">
                {work}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No future work identified</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
