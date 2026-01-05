import { useState, useEffect } from 'react';
import chatStore, { State } from './store';

// Custom hook to access the chat store state
export const useStore = (): [State, typeof chatStore] => {
  const [state, setState] = useState<State>(() => {
    // Only call getState on the client side
    if (typeof window !== 'undefined') {
      return chatStore.getState();
    }
    // Return initial state for server-side rendering
    return {
      session: null,
      activeConversation: null,
      loading: false,
      error: null,
      apiConnected: false
    };
  });

  useEffect(() => {
    // Subscribe to store updates
    const unsubscribe = chatStore.subscribe(setState);

    // Update state with actual store state after mount
    setState(chatStore.getState());

    return unsubscribe;
  }, []);

  return [state, chatStore];
};