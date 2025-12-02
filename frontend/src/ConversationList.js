import React from "react";

export default function ConversationList({
  conversations,
  onSelect,
  selectedId,
}) {
  return (
    <div className="conv-list">
      {conversations.length === 0 && (
        <div className="muted">No conversations found</div>
      )}
      {conversations.map((c) => (
        <div
          key={c.id}
          className={`conv-item ${selectedId === c.id ? "selected" : ""}`}
          onClick={() => onSelect(c)}
          title={`${c.title} — ${c.message_count} messages`}
        >
          <div className="conv-title">{c.title || "Untitled"}</div>
          <div className="conv-meta">{c.message_count} messages</div>
        </div>
      ))}
    </div>
  );
}
