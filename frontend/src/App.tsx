


import { AppProvider } from "./context/AppContext";
import LeftSidebar from "./components/LeftSidebar";
import ChatPanel from "./components/ChatPanel";
import RightConfigPanel from "./components/RightConfigPanel";

function App() {
  return (
    <AppProvider>
      <div className="flex bg-hermes-bg min-h-screen">
        <LeftSidebar />
        <ChatPanel />
        <RightConfigPanel />
      </div>
    </AppProvider>
  );
}

export default App;
