import React, { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import ChatViewer from "./ChatViewer";
import ThemeToggle from "./ThemeToggle";
import "./App.css";

const BASE_URL = "http://chat.lottotry.com:5000";
//BASE_URL = "http://127.0.0.1:5000"
function App() {
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [search, setSearch] = useState("");
  const [dark, setDark] = useState(false);

  useEffect(() => {
    fetch(`${BASE_URL}/conversations`)
      .then((res) => res.json())
      .then((data) => {
        setConversations(data);
        if (data.length > 0) setActiveId(data[0].id);
      });
  }, []);

  const filtered = conversations.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className={`layout ${dark ? "dark" : ""}`}>
      <Sidebar
        conversations={filtered}
        activeId={activeId}
        onSelect={setActiveId}
        search={search}
        setSearch={setSearch}
      />

      <ChatViewer activeId={activeId} />

      <ThemeToggle dark={dark} toggle={() => setDark(!dark)} />
    </div>
  );
}

export default App;
