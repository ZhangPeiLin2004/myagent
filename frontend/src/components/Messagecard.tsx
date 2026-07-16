


type Props = {
  role: "user" | "assistant";
  content: string;
};

export default function MessageCard({ role, content }: Props) {
  const isUser = role === "user";
  return (
    <div className={`w-full my-2 flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[70%] p-3 rounded-lg text-hermes-text ${isUser ? "bg-hermes-accent" : "bg-hermes-card"}`}>
        <pre className="whitespace-pre-wrap text-sm">{content}</pre>
      </div>
    </div>
  );
}
