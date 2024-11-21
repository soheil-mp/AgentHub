import ChatInterface from './components/Chat/ChatInterface';

function App() {
  const userId = 'test-user-123';

  return (
    <div className="min-h-screen bg-dark-500">
      <header className="bg-dark-600 border-b border-dark-400">
        <div className="max-w-[1600px] mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div>
              <h1 className="text-2xl font-bold text-accent-500">AgentHub</h1>
              <p className="text-sm text-gray-400">AI-Powered Customer Support</p>
            </div>
          </div>
          <div className="text-sm text-gray-400">
            Session ID: {userId.slice(0, 8)}...
          </div>
        </div>
      </header>
      <main className="max-w-[1600px] mx-auto p-4">
        <ChatInterface userId={userId} />
      </main>
    </div>
  );
}

export default App; 