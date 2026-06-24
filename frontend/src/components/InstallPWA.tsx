import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { Button } from './Button';

export function InstallPWA() {
  const [supportsPWA, setSupportsPWA] = useState(false);
  const [promptInstall, setPromptInstall] = useState<any>(null);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setSupportsPWA(true);
      setPromptInstall(e);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const onClick = (evt: React.MouseEvent<HTMLButtonElement>) => {
    evt.preventDefault();
    if (!promptInstall) return;
    promptInstall.prompt();
    promptInstall.userChoice.then((choiceResult: { outcome: string }) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
    });
  };

  if (!supportsPWA) return null;

  return (
    <Button 
      onClick={onClick} 
      variant="secondary" 
      className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-fuchsia-500 text-white border-0 hover:opacity-90 shadow-lg shadow-cyan-500/20"
      title="Install App"
    >
      <Download size={16} />
      <span className="hidden sm:inline font-bold">Install App</span>
    </Button>
  );
}
