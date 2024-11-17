import ChatInterface from './components/Chat/ChatInterface';

function App() {
  const userId = 'test-user-123';

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-[1600px] mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">🤖</span>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AgentHub</h1>
              <p className="text-sm text-gray-500">AI-Powered Customer Support</p>
            </div>
          </div>
          <div className="text-sm text-gray-500">
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