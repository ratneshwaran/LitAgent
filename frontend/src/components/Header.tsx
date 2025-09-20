import { Button } from '@/components/ui/button';
import { Moon, Sun, HelpCircle, BookOpen } from 'lucide-react';

interface HeaderProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export function Header({ darkMode, onToggleDarkMode }: HeaderProps) {
  return (
    <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-2 rounded-lg bg-primary/10 flex items-center justify-center" aria-hidden="true">
            <BookOpen className="w-5 h-5 text-primary" />
          </div>
          <h1 className="text-xl font-bold tracking-tight whitespace-nowrap">LitAgent</h1>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleDarkMode}
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>
          
          <Button
            variant="ghost"
            size="icon"
            aria-label="Help"
          >
            <HelpCircle className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
