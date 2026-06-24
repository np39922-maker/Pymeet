import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export interface Reaction {
  id: string;
  emoji: string;
  userId: number;
  userName: string;
  left: number;
}

const ANIMATED_EMOJIS: Record<string, string> = {
  "👍": "1f44d",
  "❤️": "2764_fe0f",
  "😂": "1f602",
  "😮": "1f62e",
  "👏": "1f44f",
  "🎉": "1f389",
};

export function ReactionsOverlay({ reactions }: { reactions: Reaction[] }) {
  const [failedEmojis, setFailedEmojis] = useState<Set<string>>(new Set());

  return (
    <div className="pointer-events-none fixed inset-0 z-50 overflow-hidden">
      <AnimatePresence>
        {reactions.map((r) => (
          <motion.div
            key={r.id}
            initial={{ opacity: 0, y: 50, scale: 0.5, x: "-50%" }}
            animate={{
              opacity: [0, 1, 1, 0],
              y: -400,
              scale: [0.5, 1.2, 1, 0.9],
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 2.5, ease: "easeOut" }}
            className="absolute bottom-0 text-7xl sm:text-6xl drop-shadow-lg flex flex-col items-center"
            style={{ left: `${r.left}vw` }}
          >
            {ANIMATED_EMOJIS[r.emoji] && !failedEmojis.has(r.emoji) ? (
              <img 
                src={`https://fonts.gstatic.com/s/e/notoemoji/latest/${ANIMATED_EMOJIS[r.emoji]}/512.gif`} 
                alt={r.emoji} 
                className="w-24 h-24 sm:w-20 sm:h-20 drop-shadow-2xl" 
                onError={() => setFailedEmojis(prev => new Set(prev).add(r.emoji))}
              />
            ) : (
              r.emoji
            )}
            <div className="mt-1 text-center text-[10px] font-bold text-white drop-shadow-md">
              {r.userName}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
