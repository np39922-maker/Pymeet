import { useState, useEffect } from 'react';
import { Download } from 'lucide-react';
import { Button } from './Button';

export function InstallPWA() {
  const [promptInstall, setPromptInstall] = useState<any>(null);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setPromptInstall(e);
    };

    window.addEventListener('beforeinstallprompt', handler);

    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const onClick = (evt: React.MouseEvent<HTMLButtonElement>) => {
    evt.preventDefault();
    if (!promptInstall) {
      alert("Installation is managed by your browser.\n\nLook for the 'Install App' icon (a small computer with a downward arrow) in your browser's address bar at the top right, or check your browser's menu (three dots) for 'Install PyMeet'.\n\nIf you don't see it, you might be using an unsupported browser, incognito mode, or the app is already installed!");
      return;
    }
    promptInstall.prompt();
    promptInstall.userChoice.then((choiceResult: { outcome: string }) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
    });
  };

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
