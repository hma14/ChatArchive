import React from "react";

export default function ConversationItem({ conversation, onClick, active }) {
  return (
    <div
      className={`conversation-item ${active ? "active" : ""}`}
      onClick={onClick}
    >
      <div className="title">{conversation.title}</div>
      <div className="time">
        {new Date(conversation.update_time * 1000).toLocaleString()}
      </div>
    </div>
  );
}
