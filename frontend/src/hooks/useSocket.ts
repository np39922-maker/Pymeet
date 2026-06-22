import { useEffect, useState } from "react";
import { io, Socket } from "socket.io-client";

const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || import.meta.env.VITE_API_URL || "";

export function useSocket(token: string | null): Socket | null {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    if (!token) return;
    
    const newSocket = io(SOCKET_URL, {
      path: "/socket.io",
      transports: ["websocket"],
      auth: { token },
      forceNew: true
    });
    
    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, [token]);

  return socket;
}
