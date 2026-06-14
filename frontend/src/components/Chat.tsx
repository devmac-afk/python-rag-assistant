import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Database, Link as LinkIcon, Loader2, Plus, Github } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

// Glass-styled Input
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-12 w-full rounded-xl glass-input px-4 py-2 text-sm text-white placeholder:text-muted-foreground focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"

// Glass-styled Button
const Button = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, variant = 'primary', ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 active:scale-95",
          variant === 'primary' 
            ? "bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 hover:brightness-110" 
            : "glass-panel hover:bg-white/10 text-foreground",
          "h-10 px-4 py-2",
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

interface Source {
  question_title: string;
  source_url: string;
  answer_url: string;
  tags: string;
}

interface Message {
  role: 'user' | 'ai';
  content: string;
  sources?: Source[];
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'ai',
      content: 'Hello! I am your Stack Overflow Python assistant. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage.content })
      });

      if (!response.ok) throw new Error('Failed to fetch response');

      const data = await response.json();
      setMessages(prev => [...prev, {
        role: 'ai',
        content: data.answer,
        sources: data.sources
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'ai',
        content: 'Error: Could not connect to the server. Please ensure the FastAPI backend is running.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatText = (text: string) => {
    const parts = text.split(/(```[\s\S]*?```)/g);
    return parts.map((part, index) => {
      if (part.startsWith('```') && part.endsWith('```')) {
        const code = part.replace(/```[a-z]*\n?/, '').replace(/```$/, '');
        return (
          <div key={index} className="relative group my-4">
            <pre className="bg-black/40 backdrop-blur-md p-4 rounded-xl overflow-x-auto border border-white/5 shadow-inner">
              <code className="text-sm text-indigo-100 font-mono leading-relaxed">{code}</code>
            </pre>
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <span className="text-[10px] text-muted-foreground uppercase font-bold bg-black/50 px-2 py-1 rounded">Code</span>
            </div>
          </div>
        );
      }
      
      const inlineParts = part.split(/(`[^`]+`)/g);
      return (
        <p key={index} className="leading-relaxed mb-4 last:mb-0">
          {inlineParts.map((inlinePart, i) => {
            if (inlinePart.startsWith('`') && inlinePart.endsWith('`')) {
              return <code key={i} className="bg-indigo-500/10 text-indigo-300 px-1.5 py-0.5 rounded-md text-xs font-mono border border-indigo-500/20">{inlinePart.slice(1, -1)}</code>;
            }
            return <span key={i} dangerouslySetInnerHTML={{ __html: inlinePart.replace(/\n/g, '<br/>') }} />;
          })}
        </p>
      );
    });
  };

  return (
    <div className="flex h-screen w-full bg-transparent text-foreground relative overflow-hidden">
      
      {/* Sidebar */}
      <aside className="hidden lg:flex flex-col w-[280px] h-full glass-panel border-r-0 z-20">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Database className="text-white w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-white leading-tight">StackAI</h1>
              <p className="text-[10px] text-indigo-300/60 uppercase tracking-widest font-black">Python Expert</p>
            </div>
          </div>

          <Button className="w-full justify-start gap-2 mb-6" onClick={() => setMessages([{ role: 'ai', content: 'Hello! I am your Stack Overflow Python assistant. How can I help you today?' }])}>
            <Plus className="w-4 h-4" /> New Chat
          </Button>
        </div>

        <div className="mt-auto p-6 space-y-4">
          <div className="flex items-center gap-3 px-3 py-2 rounded-2xl bg-white/5 border border-white/5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500/20 to-purple-600/20 flex items-center justify-center border border-indigo-500/30">
              <User className="w-4 h-4 text-indigo-300" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="text-xs font-medium text-white truncate">Developer Mode</p>
              <p className="text-[10px] text-muted-foreground truncate">pro-tier</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col h-full relative">
        
        {/* Header (Mobile-ish or just top-bar) */}
        <header className="flex items-center justify-between px-6 py-4 glass-panel border-t-0 border-l-0 border-r-0 z-10 lg:bg-transparent lg:backdrop-blur-none lg:border-none">
          <div className="flex items-center gap-3 lg:hidden">
            <Database className="text-indigo-500 w-6 h-6" />
            <h1 className="font-bold text-white">StackAI</h1>
          </div>
          <div className="hidden lg:block">
            <span className="text-xs font-medium text-indigo-300/60 flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              RAG PIPELINE ACTIVE • GROQ ENGINE
            </span>
          </div>
          <div className="flex items-center gap-3">
             <button className="p-2 rounded-xl glass-panel hover:bg-white/10 transition-colors">
              <Github className="w-5 h-5 text-white" />
            </button>
          </div>
        </header>

        {/* Chat Scroll Area */}
        <div className="flex-1 overflow-y-auto pt-8 pb-32">
          <div className="max-w-3xl mx-auto px-6 space-y-8">
            <AnimatePresence initial={false}>
              {messages.map((msg, idx) => (
                <motion.div 
                  key={idx} 
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ type: "spring", duration: 0.5, bounce: 0.3 }}
                  className={cn("flex w-full group", msg.role === 'user' ? "justify-end" : "justify-start")}
                >
                  <div className={cn("flex gap-4 max-w-[85%]", msg.role === 'user' ? "flex-row-reverse" : "flex-row")}>
                    
                    {/* Avatar */}
                    <div className={cn(
                      "flex-shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg transition-transform group-hover:scale-110",
                      msg.role === 'user' 
                        ? "bg-white/10 border border-white/20" 
                        : "bg-gradient-to-br from-indigo-500 to-purple-600 border border-white/20"
                    )}>
                      {msg.role === 'user' ? <User className="w-5 h-5 text-white" /> : <Bot className="w-5 h-5 text-white" />}
                    </div>

                    {/* Message Bubble */}
                    <div className="flex flex-col gap-3">
                      <div className={cn(
                        "p-5 rounded-2xl text-[15px] shadow-2xl relative overflow-hidden",
                        msg.role === 'user' 
                          ? "bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-tr-sm" 
                          : "glass-panel text-indigo-50 rounded-tl-sm border-white/10"
                      )}>
                        {msg.role === 'ai' && (
                          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 blur-3xl rounded-full -mr-16 -mt-16 pointer-events-none"></div>
                        )}
                        {formatText(msg.content)}
                      </div>

                      {/* Sources */}
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
                          {msg.sources.map((src, i) => (
                            <motion.a 
                              whileHover={{ y: -2 }}
                              key={i} 
                              href={src.source_url} 
                              target="_blank" 
                              rel="noreferrer"
                              className="flex flex-col p-4 rounded-xl glass-panel hover:bg-white/10 transition-all group/source"
                            >
                              <div className="flex items-center gap-2 mb-2">
                                <LinkIcon className="w-3 h-3 text-indigo-400" />
                                <span className="text-[10px] font-black text-indigo-300/60 uppercase tracking-widest truncate">Stack Overflow</span>
                              </div>
                              <span className="text-sm font-semibold text-white group-hover/source:text-indigo-300 transition-colors line-clamp-2 leading-snug">
                                {src.question_title}
                              </span>
                              <div className="flex flex-wrap gap-1 mt-3">
                                {src.tags.split(',').map((tag, tagIdx) => (
                                  <span key={tagIdx} className="text-[9px] px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 font-bold uppercase tracking-tighter">
                                    {tag.trim()}
                                  </span>
                                ))}
                              </div>
                            </motion.a>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            
            {isLoading && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex w-full justify-start"
              >
                <div className="flex gap-4 max-w-[80%]">
                  <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 border border-white/20 animate-pulse">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="p-5 rounded-2xl glass-panel flex items-center gap-3 text-indigo-200">
                    <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
                    <span className="text-sm font-medium">Synthesizing Python wisdom...</span>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={endOfMessagesRef} />
          </div>
        </div>

        {/* Input Area Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6 pointer-events-none">
          <div className="max-w-3xl mx-auto pointer-events-auto">
            <div className="glass-panel p-2 rounded-2xl shadow-2xl relative">
              <form onSubmit={handleSubmit} className="flex gap-2 relative">
                <Input 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask any Python question..." 
                  className="flex-1 pr-14 bg-transparent border-none h-14 text-base"
                  disabled={isLoading}
                />
                <Button 
                  type="submit" 
                  disabled={isLoading || !input.trim()}
                  className="absolute right-2 top-2 h-10 w-10 p-0 rounded-xl"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </Button>
              </form>
            </div>
            <p className="text-center text-[10px] text-muted-foreground/60 mt-3 font-medium uppercase tracking-widest">
              AI can hallucinate. Verify critical code.
            </p>
          </div>
        </div>
      </main>

      {/* Aesthetic Accents */}
      <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-600/10 blur-[120px] rounded-full -z-10 animate-pulse"></div>
      <div className="fixed bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-purple-600/10 blur-[120px] rounded-full -z-10 animate-pulse"></div>

    </div>
  );
}
