-- Customer table
CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    subscription_tier TEXT CHECK(subscription_tier IN ('free', 'pro', 'enterprise')) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Support tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    status TEXT CHECK(status IN ('open', 'in_progress', 'resolved', 'escalated')) DEFAULT 'open',
    intent TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Conversation history table
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL,
    message_role TEXT CHECK(message_role IN ('user', 'assistant', 'system')) NOT NULL,
    message_content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);

-- Knowledge base table (for FAQ)
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample knowledge base entries
INSERT INTO knowledge_base (category, question, answer, keywords) VALUES
('billing', 'How do I upgrade my plan?', 'You can upgrade your plan by going to Settings > Subscription > Upgrade Plan. Pro plan costs $29/month and Enterprise costs $99/month.', 'upgrade, plan, billing, subscription'),
('technical', 'How do I reset my password?', 'Click "Forgot Password" on the login page. You''ll receive an email with a reset link. The link expires in 24 hours.', 'password, reset, login, account'),
('account', 'How do I delete my account?', 'Please contact support to delete your account. We''ll need to verify your identity first.', 'delete, account, cancel'),
('technical', 'The app is slow, what should I do?', 'Try clearing your browser cache. If issues persist, check our status page at status.saasapp.com', 'slow, performance, speed');