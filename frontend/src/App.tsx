import ChatInterface from './components/Chat/ChatInterface';

function App() {
  // In a real app, this would come from authentication
  const userId = 'test-user-123';

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto p-4">
          <h1 className="text-2xl font-bold text-gray-900">🤖 AgentHub Chat</h1>
        </div>
      </header>
      <main className="max-w-4xl mx-auto p-4">
        <ChatInterface userId={userId} />
      </main>
    </div>
  );
}

export default App; 