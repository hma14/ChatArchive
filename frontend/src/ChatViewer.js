import React, { useEffect, useState, useRef } from "react";
import ChatMessage from "./ChatMessage";
import { scrollToBottom } from "./utils/scroll";
import { BASE_URL } from "./App";

export default function ChatViewer({ activeId }) {
  const [messages, setMessages] = useState([]);
  const container = useRef(null);

  useEffect(() => {
    if (!activeId) return;

    fetch(`${BASE_URL}/conversation/${activeId}`)
      .then((res) => res.json())
      .then((data) => {
        setMessages(data);
        setTimeout(() => scrollToBottom(container), 50);
      });
  }, [activeId]);

  return (
    <div className="chat-container" ref={container}>
      {messages.map((m) => (
        <ChatMessage
          key={m.id}
          role={m.role} // ← REAL FIELDS from backend
          content={m.text} // ← REAL FIELDS from backend
        />
      ))}
    </div>
  );
}
