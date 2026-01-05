import React from 'react';
import Layout from '@theme/Layout';
import ChatContainer from '../../components/chat/ChatContainer';
import '../../css/chat-styles.css';

function ChatPage() {
  return (
    <Layout title="AI Knowledge Assistant" description="Chat with our AI assistant">
      <ChatContainer />
    </Layout>
  );
}

export default ChatPage;