import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useUIStore } from '@/lib/store';
import { DISCIPLINES, STUDY_TYPES, PROVIDERS } from '@/lib/types';
import { X } from 'lucide-react';

export function AdvancedFilters() {
  const { advancedOpen, filters, setFilters } = useUIStore();

  if (!advancedOpen) return null;

  const addToArray = (field: keyof typeof filters, value: string) => {
    if (!value.trim()) return;
    const current = (filters[field] as string[]) || [];
    if (!current.includes(value)) {
      setFilters({ [field]: [...current, value] });
    }
  };

  const removeFromArray = (field: keyof typeof filters, value: string) => {
    const current = (filters[field] as string[]) || [];
    setFilters({ [field]: current.filter(item => item !== value) });
  };


  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="text-lg">Advanced Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Time Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Start Year</label>
            <Input
              type="number"
              placeholder="e.g., 2020"
              value={filters.startYear || ''}
              onChange={(e) => setFilters({ startYear: e.target.value ? parseInt(e.target.value) : undefined })}
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">End Year</label>
            <Input
              type="number"
              placeholder="e.g., 2024"
              value={filters.endYear || ''}
              onChange={(e) => setFilters({ endYear: e.target.value ? parseInt(e.target.value) : undefined })}
            />
          </div>
        </div>

        {/* Disciplines */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Disciplines</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(filters.disciplines || []).map((discipline) => (
              <Badge key={discipline} variant="secondary" className="flex items-center gap-1">
                {discipline}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => removeFromArray('disciplines', discipline)}
                />
              </Badge>
            ))}
          </div>
          <Select onValueChange={(value) => addToArray('disciplines', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select disciplines..." />
            </SelectTrigger>
            <SelectContent>
              {DISCIPLINES.map((discipline) => (
                <SelectItem key={discipline} value={discipline}>
                  {discipline}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Study Types */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Study Types</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(filters.studyTypes || []).map((studyType) => (
              <Badge key={studyType} variant="secondary" className="flex items-center gap-1">
                {studyType}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => removeFromArray('studyTypes', studyType)}
                />
              </Badge>
            ))}
          </div>
          <Select onValueChange={(value) => addToArray('studyTypes', value)}>
            <SelectTrigger>
              <SelectValue placeholder="Select study types..." />
            </SelectTrigger>
            <SelectContent>
              {STUDY_TYPES.map((studyType) => (
                <SelectItem key={studyType} value={studyType}>
                  {studyType}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Methods */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Methods</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(filters.methods || []).map((method) => (
              <Badge key={method} variant="secondary" className="flex items-center gap-1">
                {method}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => removeFromArray('methods', method)}
                />
              </Badge>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., difference-in-differences, PCR, fMRI"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addToArray('methods', e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            <Button 
              variant="outline" 
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                addToArray('methods', input.value);
                input.value = '';
              }}
            >
              Add
            </Button>
          </div>
        </div>

        {/* Population/Corpus */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Population/Corpus</label>
          <Input
            placeholder="e.g., humans, adults, K-12, EU firms, Latin manuscripts"
            value={filters.population || ''}
            onChange={(e) => setFilters({ population: e.target.value })}
          />
        </div>

        {/* Geography/Setting */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Geography/Setting</label>
          <Input
            placeholder="e.g., United States, Europe, urban, rural"
            value={filters.geography || ''}
            onChange={(e) => setFilters({ geography: e.target.value })}
          />
        </div>

        {/* Languages */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Languages</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(filters.languages || []).map((language) => (
              <Badge key={language} variant="secondary" className="flex items-center gap-1">
                {language}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => removeFromArray('languages', language)}
                />
              </Badge>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., en, es, fr, de, zh"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addToArray('languages', e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            <Button 
              variant="outline" 
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                addToArray('languages', input.value);
                input.value = '';
              }}
            >
              Add
            </Button>
          </div>
        </div>

        {/* Venues */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Venues</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(filters.venues || []).map((venue) => (
              <Badge key={venue} variant="secondary" className="flex items-center gap-1">
                {venue}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => removeFromArray('venues', venue)}
                />
              </Badge>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., Nature, Science, JAMA, NeurIPS"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addToArray('venues', e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            <Button 
              variant="outline" 
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                addToArray('venues', input.value);
                input.value = '';
              }}
            >
              Add
            </Button>
          </div>
        </div>

        {/* Access Preferences */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Access Preferences</label>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filters.access?.peerReviewed ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                access: { ...filters.access, peerReviewed: !filters.access?.peerReviewed }
              })}
            >
              Peer-reviewed only
            </Button>
            <Button
              variant={filters.access?.preprints ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                access: { ...filters.access, preprints: !filters.access?.preprints }
              })}
            >
              Preprints allowed
            </Button>
            <Button
              variant={filters.access?.openAccess ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                access: { ...filters.access, openAccess: !filters.access?.openAccess }
              })}
            >
              Open access only
            </Button>
          </div>
        </div>

        {/* Evidence Quality */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Evidence Quality</label>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filters.evidence?.prereg ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                evidence: { ...filters.evidence, prereg: !filters.evidence?.prereg }
              })}
            >
              Preregistered
            </Button>
            <Button
              variant={filters.evidence?.data ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                evidence: { ...filters.evidence, data: !filters.evidence?.data }
              })}
            >
              Data available
            </Button>
            <Button
              variant={filters.evidence?.code ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                evidence: { ...filters.evidence, code: !filters.evidence?.code }
              })}
            >
              Code available
            </Button>
            <Button
              variant={filters.evidence?.ethics ? "default" : "outline"}
              size="sm"
              onClick={() => setFilters({
                evidence: { ...filters.evidence, ethics: !filters.evidence?.ethics }
              })}
            >
              Ethics approved
            </Button>
          </div>
        </div>

        {/* Exclude Keywords */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Exclude Keywords</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {(filters.exclude || []).map((keyword) => (
              <Badge key={keyword} variant="destructive" className="flex items-center gap-1">
                {keyword}
                <X 
                  className="w-3 h-3 cursor-pointer" 
                  onClick={() => removeFromArray('exclude', keyword)}
                />
              </Badge>
            ))}
          </div>
          <div className="flex gap-2">
            <Input
              placeholder="e.g., animals, survey, review"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addToArray('exclude', e.currentTarget.value);
                  e.currentTarget.value = '';
                }
              }}
            />
            <Button 
              variant="outline" 
              onClick={(e) => {
                const input = e.currentTarget.previousElementSibling as HTMLInputElement;
                addToArray('exclude', input.value);
                input.value = '';
              }}
            >
              Add
            </Button>
          </div>
        </div>

        {/* Limit and Providers */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Result Limit</label>
            <Select 
              value={filters.limit?.toString() || '20'} 
              onValueChange={(value) => setFilters({ limit: parseInt(value) })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
                <SelectItem value="100">100</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Sources</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {(filters.providers || []).map((provider) => (
                <Badge key={provider} variant="secondary" className="flex items-center gap-1">
                  {provider}
                  <X 
                    className="w-3 h-3 cursor-pointer" 
                    onClick={() => removeFromArray('providers', provider)}
                  />
                </Badge>
              ))}
            </div>
            <Select onValueChange={(value) => addToArray('providers', value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select sources..." />
              </SelectTrigger>
              <SelectContent>
                {PROVIDERS.map((provider) => (
                  <SelectItem key={provider} value={provider}>
                    {provider}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
