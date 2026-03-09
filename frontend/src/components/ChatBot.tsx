import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Loader2 } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'https://tariffnavigator-backend.onrender.com/api/v1';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface SuggestedAction {
  type: string;
  label: string;
  data: any;
}

export const ChatBot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hi! I'm your TariffNavigator assistant. I can help you find HS codes, explain tariff rates, and guide you through using the app. What would you like to know?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedActions, setSuggestedActions] = useState<SuggestedAction[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (messageText?: string) => {
    const textToSend = messageText || input.trim();
    if (!textToSend || isLoading) return;

    // Add user message
    const newMessages: Message[] = [...messages, { role: 'user', content: textToSend }];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);
    setSuggestedActions([]);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: textToSend,
        history: messages.slice(-10) // Send last 10 messages for context
      });

      // Add assistant response
      setMessages([...newMessages, {
        role: 'assistant',
        content: response.data.response
      }]);

      // Set suggested actions if any
      if (response.data.suggested_actions) {
        setSuggestedActions(response.data.suggested_actions);
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      setMessages([...newMessages, {
        role: 'assistant',
        content: error.response?.data?.detail || "Sorry, I'm having trouble responding right now. Please try again."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickQuestions = [
    "What's the HS code for laptops?",
    "How do I calculate tariffs?",
    "What's the difference between CN and EU rates?",
    "How do I create a watchlist?"
  ];

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 text-white p-4 rounded-2xl z-50 transition-all duration-300 hover:scale-110 active:scale-95"
          style={{background: 'linear-gradient(135deg, #1E3A5F, #264875)',
                  boxShadow: '0 8px 24px rgba(30,58,95,0.35), 0 0 0 1px rgba(255,255,255,0.1)'}}
          aria-label="Open chat"
        >
          <MessageCircle className="w-6 h-6" />
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[580px] bg-white rounded-2xl flex flex-col z-50 animate-in overflow-hidden"
             style={{boxShadow: '0 24px 60px rgba(30,58,95,0.20), 0 0 0 1px rgba(0,0,0,0.06)'}}>
          {/* Header */}
          <div className="text-white p-4 flex items-center justify-between flex-shrink-0"
               style={{background: 'linear-gradient(135deg, #152B47 0%, #1E3A5F 100%)'}}>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                   style={{background: 'linear-gradient(135deg, #0D9488, #14B8A6)',
                           boxShadow: '0 0 12px rgba(13,148,136,0.4)'}}>
                <MessageCircle className="w-4 h-4 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-sm">TariffNavigator AI</h3>
                <p className="text-[11px] text-blue-300 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-brand-teal inline-block" />
                  Online — 2026 tariff rates
                </p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)}
                    className="text-blue-300 hover:text-white hover:bg-white/10 p-1.5 rounded-lg transition-all"
                    aria-label="Close chat">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50/50">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[82%] rounded-2xl px-3.5 py-2.5 text-sm ${
                  msg.role === 'user'
                    ? 'text-white rounded-br-sm'
                    : 'bg-white text-gray-800 border border-gray-100 shadow-sm rounded-bl-sm'
                }`}
                style={msg.role === 'user' ? {background: 'linear-gradient(135deg, #1E3A5F, #264875)'} : {}}>
                  <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-100 shadow-sm rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2">
                  <div className="flex gap-1">
                    {[0,1,2].map(i => (
                      <div key={i} className="w-1.5 h-1.5 rounded-full bg-brand-blue animate-bounce"
                           style={{animationDelay: `${i * 150}ms`}} />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {suggestedActions.length > 0 && (
              <div className="space-y-1.5">
                <p className="text-[11px] text-gray-400 font-medium uppercase tracking-wide">Suggested</p>
                {suggestedActions.map((action, idx) => (
                  <button key={idx}
                    onClick={() => { const params = new URLSearchParams(action.data).toString(); window.location.href = `/calculator?${params}`; }}
                    className="w-full text-left text-sm bg-white hover:bg-blue-50 text-brand-navy p-2.5 rounded-xl border border-gray-100 hover:border-brand-blue/30 transition-all font-medium shadow-sm">
                    → {action.label}
                  </button>
                ))}
              </div>
            )}

            {messages.length === 1 && (
              <div className="space-y-1.5">
                <p className="text-[11px] text-gray-400 font-medium uppercase tracking-wide">Try asking</p>
                {quickQuestions.map((question, idx) => (
                  <button key={idx} onClick={() => sendMessage(question)}
                    className="w-full text-left text-sm bg-white hover:bg-blue-50 text-gray-700 px-3 py-2 rounded-xl border border-gray-100 hover:border-brand-blue/30 transition-all shadow-sm">
                    {question}
                  </button>
                ))}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-100 p-3 bg-white flex-shrink-0">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about tariffs, HTS codes…"
                className="flex-1 border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all bg-gray-50"
                style={{boxShadow: 'none'}}
                disabled={isLoading}
              />
              <button onClick={() => sendMessage()}
                disabled={!input.trim() || isLoading}
                className="text-white p-2.5 rounded-xl disabled:opacity-40 transition-all hover:opacity-90 active:scale-95 flex-shrink-0"
                style={{background: 'linear-gradient(135deg, #0D9488, #14B8A6)'}}
                aria-label="Send">
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
