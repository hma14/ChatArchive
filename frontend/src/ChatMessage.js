import ChatGPTIcon from "./assets/chatgpt.svg"; // or .svg

export default function ChatMessage({ role, content }) {
  const isAssistant = role === "assistant";
  const isUser = role === "user";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: isAssistant ? "row" : "row-reverse",
        alignItems: "flex-start",
        marginBottom: "20px",
        width: "100%",
      }}
    >
      {/* ==== Avatar ==== */}
      {isAssistant ? (
        <img
          src={ChatGPTIcon}
          alt="assistant"
          style={{
            width: 40,
            height: 40,
            borderRadius: "50%",
            marginRight: 10,
          }}
        />
      ) : (
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: "50%",
            backgroundColor: "#007bff",
            color: "white",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontWeight: "bold",
            marginLeft: 10,
          }}
        >
          U
        </div>
      )}

      {/* ==== Message Bubble ==== */}
      <div
        style={{
          background: isAssistant ? "#f7f7f8" : "#d0e7ff",
          padding: "12px 16px",
          borderRadius: 10,
          maxWidth: "70%",
          whiteSpace: "pre-wrap",
        }}
      >
        {content}
      </div>
    </div>
  );
}
