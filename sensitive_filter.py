"""
Sensitive Data Filter for FTS5 Indexer
Filters out messages containing passwords, tokens, private keys, etc.
"""

import re
from typing import List, Tuple

# Patterns to detect sensitive data
SENSITIVE_PATTERNS = [
    # API keys and tokens
    (r'(api[_-]?key|apikey|api[_-]?secret)', 'api_key'),
    (r'(bearer|Authorization)[:\s]+[A-Za-z0-9\-_]+', 'auth_header'),
    (r'x-api-key', 'api_key'),
    (r'x[_-]?api[_-]?key', 'api_key'),
    
    # Passwords
    (r'password|passwd|pwd', 'password'),
    (r'secret[_-]?key|secretkey', 'secret'),
    
    # Crypto
    (r'private[_-]?key|privkey', 'private_key'),
    (r'0x[a-fA-F0-9]{40,}', 'wallet_address'),
    (r'[a-fA-F0-9]{64}', 'hex_key'),  # Long hex strings
    
    # Bot tokens (Discord, Telegram, etc.)
    (r'[MN][A-Za-z\d]{23,}\.[A-Za-z\d_-]{6,}\.[A-Za-z\d_-]{27,}', 'bot_token'),
    (r'\d{8,10}:[A-Za-z\d_-]{35,}', 'bot_token'),
    (r'TG[A-Za-z0-9]{20,}', 'telegram_token'),
    
    # Database
    (r'mysql://[^\s]+', 'db_connection'),
    (r'postgresql://[^\s]+', 'db_connection'),
    (r'redis://[^\s]+', 'redis_connection'),
    
    # SSH
    (r'-----BEGIN.*?PRIVATE KEY-----', 'private_key'),
    (r'ssh-rsa\s+AAAA[^\s]+', 'ssh_key'),
    
    # Generic high-entropy strings (potential keys)
    (r'[A-Za-z0-9+/]{40,}={0,2}', 'potential_key'),
]

# Exact match forbidden terms
FORBIDDEN_EXACT = [
    'token',
    'secret',
    'password',
    'private',
    'api_key',
]

# Minimum entropy threshold for "potential key" detection
MIN_KEY_LENGTH = 32


def contains_sensitive(content: str) -> Tuple[bool, List[str]]:
    """
    Check if content contains sensitive data.
    
    Returns:
        (is_sensitive, list_of_detected_types)
    """
    if not content or len(content) < 8:
        return False, []
    
    detected = []
    content_lower = content.lower()
    
    # Check exact forbidden terms (with boundaries)
    for term in FORBIDDEN_EXACT:
        # Must be a standalone word, not part of another word
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, content_lower, re.IGNORECASE):
            detected.append(term)
    
    # Check regex patterns
    for pattern, label in SENSITIVE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            if label not in detected:
                detected.append(label)
    
    # Check for high-entropy strings (potential keys)
    # Long base64-like strings
    if re.search(r'[A-Za-z0-9+/]{50,}={0,2}', content):
        if 'potential_key' not in detected:
            detected.append('potential_key')
    
    # Long hex strings
    if re.search(r'[a-fA-F0-9]{64,}', content):
        if 'hex_key' not in detected:
            detected.append('hex_key')
    
    return len(detected) > 0, detected


def mask_sensitive(content: str) -> str:
    """
    Mask sensitive data in content for safe display.
    """
    if not content:
        return content
    
    masked = content
    
    # Mask bot tokens (Discord, Telegram, etc.)
    masked = re.sub(
        r'[MN][A-Za-z\d]{23,}\.[A-Za-z\d_-]{6,}\.[A-Za-z\d_-]{27,}',
        '[DISCORD_BOT_TOKEN]',
        masked
    )
    masked = re.sub(
        r'\d{8,10}:[A-Za-z\d_-]{35,}',
        '[BOT_TOKEN]',
        masked
    )
    masked = re.sub(
        r'TG[A-Za-z0-9]{20,}',
        '[TELEGRAM_TOKEN]',
        masked
    )
    
    # Mask API keys
    masked = re.sub(
        r'(api[_-]?key[:\s=]+)[A-Za-z0-9\-_]{20,}',
        r'\1[API_KEY_MASKED]',
        masked,
        flags=re.IGNORECASE
    )
    
    # Mask private keys
    masked = re.sub(
        r'-----BEGIN.*?PRIVATE KEY-----[\s\S]*?-----END.*?PRIVATE KEY-----',
        '[PRIVATE_KEY_MASKED]',
        masked
    )
    
    # Mask long hex strings
    masked = re.sub(
        r'[a-fA-F0-9]{64,}',
        '[HEX_KEY_MASKED]',
        masked
    )
    
    return masked


# Quick test
if __name__ == "__main__":
    test_cases = [
        ("我的 API Key 是 sk-cp-xxx123456789", True, "api_key"),
        ("password: mysecretpassword123", True, "password"),
        ("Discord Token: MTIzNDU2Nzg5OTYxNDMyNTky.G0QLMA.abc123xyz", True, "bot_token"),
        ("TG123456789:AAbbccddEEffggHH", True, "bot_token"),
        ("今天天氣很好，我們討論 FTS5 吧", False, None),
        ("我的錢包地址是 0x71C7656EC7ab88b098defB751", False, "wallet"),  # Short, not a key
    ]
    
    print("🧪 Testing Sensitive Data Filter...")
    for content, expected_detect, expected_type in test_cases:
        detected, types = contains_sensitive(content)
        status = "✅" if detected == expected_detect else "❌"
        print(f"  {status} \"{content[:40]}...\"")
        print(f"      Detected: {detected}, Types: {types}")
