import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import ChatGPTIcon from "./assets/chatgpt.svg";

export default function ChatMessage({ message }) {
  const isUser = message.author === "user";

  return (
    <div className={isUser ? "msg-row user" : "msg-row assistant"}>
      {!isUser && <img src="/gpt.png" alt="assistant" className="avatar" />}

      {isUser && <img src="/user.png" alt="user" className="avatar" />}

      <div className="msg-bubble">
        <ReactMarkdown
          children={message.text}
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[]}
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || "");
              return !inline && match ? (
                <SyntaxHighlighter language={match[1]} PreTag="div">
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              ) : (
                <code className="inline-code" {...props}>
                  {children}
                </code>
              );
            },
          }}
        />
      </div>
    </div>
  );
}
