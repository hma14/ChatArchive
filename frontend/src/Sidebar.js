import React from "react";
import ConversationItem from "./ConversationItem";
import SearchBar from "./SearchBar";

export default function Sidebar({
  conversations,
  onSelect,
  activeId,
  search,
  setSearch,
}) {
  return (
    <div className="sidebar">
      <SearchBar search={search} setSearch={setSearch} />

      <div className="sidebar-list">
        {conversations.map((c) => (
          <ConversationItem
            key={c.id}
            conversation={c}
            active={c.id === activeId}
            onClick={() => onSelect(c.id)}
          />
        ))}
      </div>
    </div>
  );
}
