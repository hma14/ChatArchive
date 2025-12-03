import React from "react";
import { marked } from "marked";
import "./ChatMessage.css"; // make sure this path is correct
import chatgptIcon from "./assets/chatgpt.svg";
import userIcon from "./assets/lottotry-favicon.ico";

export default function ChatMessage({ role, content }) {
  // Convert markdown → HTML
  const html = marked.parse(content || "");
  const avatar = role === "assistant" ? chatgptIcon : userIcon;
  return (
    <div className={`chat-message ${role}`}>
      {/* Avatar */}
      <div
        className="avatar"
        style={{
          backgroundImage: `url(${avatar})`,
        }}
        /* style={{
          display: "flex",
          flexDirection: "row",
          backgroundImage: role === "assistant" ? chatgptIcon : userIcon,
        }} */
      />

      {/* Message bubble */}
      <div className="bubble" dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}
