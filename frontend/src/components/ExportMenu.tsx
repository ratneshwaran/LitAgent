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
        <CardTitle className="text-lg flex items-center gap-2">
          <Download className="w-5 h-5" />
          Export Results
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {exportFormats.map((format) => {
            const Icon = format.icon;
            const isExporting = exporting === format.key;
            const isExported = exported.has(format.key);
            
            return (
              <Button
                key={format.key}
                variant="outline"
                className="h-auto p-4 flex flex-col items-start gap-2"
                onClick={() => handleExport(format.key)}
                disabled={isExporting}
              >
                <div className="flex items-center gap-2 w-full">
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{format.label}</span>
                  {isExporting && <Loader2 className="w-4 h-4 animate-spin ml-auto" />}
                  {isExported && <CheckCircle className="w-4 h-4 text-green-500 ml-auto" />}
                </div>
                <p className="text-xs text-muted-foreground text-left">
                  {format.description}
                </p>
              </Button>
            );
          })}
        </div>

        {/* Export Summary */}
        <div className="mt-4 p-3 bg-muted/50 rounded-lg">
          <div className="text-sm text-muted-foreground">
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
