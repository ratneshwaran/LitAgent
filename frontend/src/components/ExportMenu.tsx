import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ParsedQuery, SearchResponse } from '@/lib/types';
import { exportResults, downloadBlob } from '@/lib/api';
import { 
  Download, 
  FileText, 
  FileCode, 
  FileSpreadsheet, 
  FileJson, 
  File,
  CheckCircle,
  Loader2
} from 'lucide-react';

interface ExportMenuProps {
  query: ParsedQuery;
  results: SearchResponse;
}

export function ExportMenu({ query, results }: ExportMenuProps) {
  const [exporting, setExporting] = useState<string | null>(null);
  const [exported, setExported] = useState<Set<string>>(new Set());

  const exportFormats = [
    {
      key: 'markdown',
      label: 'Markdown',
      icon: FileText,
      description: 'Executive summary + table',
      extension: 'md'
    },
    {
      key: 'bibtex',
      label: 'BibTeX',
      icon: FileCode,
      description: 'For reference managers (Zotero, EndNote)',
      extension: 'bib'
    },
    {
      key: 'ris',
      label: 'RIS',
      icon: FileCode,
      description: 'Reference manager format',
      extension: 'ris'
    },
    {
      key: 'json',
      label: 'JSON',
      icon: FileJson,
      description: 'Raw data records',
      extension: 'json'
    },
    {
      key: 'csv',
      label: 'CSV',
      icon: FileSpreadsheet,
      description: 'Spreadsheet format',
      extension: 'csv'
    },
    {
      key: 'pdf',
      label: 'PDF',
      icon: File,
      description: 'Print-ready summary',
      extension: 'pdf'
    }
  ];

  const handleExport = async (format: string) => {
    setExporting(format);
    try {
      const blob = await exportResults(
        format as 'markdown' | 'bibtex' | 'ris' | 'json' | 'csv' | 'pdf',
        query,
        results
      );
      
      const formatInfo = exportFormats.find(f => f.key === format);
      const filename = `litagent-results-${Date.now()}.${formatInfo?.extension}`;
      
      downloadBlob(blob, filename);
      setExported(prev => new Set([...prev, format]));
      
      // Reset exported state after 3 seconds
      setTimeout(() => {
        setExported(prev => {
          const newSet = new Set(prev);
          newSet.delete(format);
          return newSet;
        });
      }, 3000);
    } catch (error) {
      console.error(`Export failed for ${format}:`, error);
      // TODO: Show error toast
    } finally {
      setExporting(null);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2 flex-wrap">
          <Download className="w-5 h-5" />
          Export Results
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
          {exportFormats.map((format) => {
            const Icon = format.icon;
            const isExporting = exporting === format.key;
            const isExported = exported.has(format.key);

            return (
              <div key={format.key} className="flex flex-col items-center justify-start">
                <Button
                  variant="outline"
                  className="aspect-square w-full max-w-[100px] flex items-center justify-center p-0"
                  onClick={() => handleExport(format.key)}
                  disabled={isExporting}
                  aria-label={`Export ${format.label}`}
                  title={`Export ${format.label}`}
                >
                  {isExporting ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                  ) : (
                    <Icon className="w-7 h-7" />
                  )}
                </Button>
                <div className="mt-2 text-xs font-medium text-center truncate w-full" title={format.label}>
                  {format.label}
                  {isExported && <CheckCircle className="inline-block w-3 h-3 text-green-500 ml-1 align-text-top" />}
                </div>
              </div>
            );
          })}
        </div>

        {/* Export Summary */}
        <div className="mt-4 p-3 bg-muted/50 rounded-lg">
          <div className="text-sm text-muted-foreground break-words whitespace-normal">
            <strong>Export includes:</strong>
            <ul className="mt-1 space-y-1">
              <li>• {results.summary.total} papers from {results.summary.sources.length} sources</li>
              <li>• Search query and filters applied</li>
              <li>• Key insights and research gaps</li>
              <li>• Full paper metadata and abstracts</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
