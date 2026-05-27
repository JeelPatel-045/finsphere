import MainLayout from "@/components/layout/MainLayout";

import ChatWindow from "@/components/chat/ChatWindow";
import PromptInput from "@/components/chat/PromptInput";
import SuggestedPrompts from "@/components/chat/SuggestedPrompts";

import AgentActivityFeed from "@/components/agents/AgentActivityFeed";

export default function ChatPage() {
  return (
    <MainLayout
      title="AI Finance Copilot"
      description="Multi-agent financial reasoning and autonomous workflow execution"
    >
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* LEFT */}
        <div className="xl:col-span-2 space-y-6">
          
          <SuggestedPrompts />

          <ChatWindow />

          <PromptInput />
        </div>

        {/* RIGHT */}
        <div>
          <AgentActivityFeed />
        </div>
      </div>
    </MainLayout>
  );
}