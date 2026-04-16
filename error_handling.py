"""
Error Handling and Fallback Module for FTS5/LLM
Three-layer fallback strategy for robust error recovery.
"""

import time
import logging
from typing import Dict, List, Any, Optional
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

# Error types
class FTS5Error(Exception):
    """Base exception for FTS5 errors."""
    pass

class RateLimitError(FTS5Error):
    """Rate limit exceeded."""
    pass

class APITimeoutError(FTS5Error):
    """API request timed out."""
    pass

class APIServerError(FTS5Error):
    """Server error from API provider."""
    pass

class NetworkError(FTS5Error):
    """Network connectivity error."""
    pass


# Configuration
MAX_RETRIES = 2
RATE_LIMIT_WAIT = 5  # seconds
SERVER_ERROR_WAIT = 10  # seconds
TIMEOUT_SECONDS = 30


def simple_template_summary(results: List[Dict[str, Any]]) -> str:
    """
    Layer 2 Fallback: Generate simple template summary without LLM.
    Used when LLM API is unavailable.
    """
    if not results:
        return "找不到相關的對話記錄。"
    
    # Group by sender
    user_msgs = [r for r in results if r.get('sender') == 'user']
    assistant_msgs = [r for r in results if r.get('sender') == 'assistant']
    
    # Build simple summary
    lines = []
    lines.append(f"找到 {len(results)} 條相關記錄：")
    lines.append("")
    
    if user_msgs:
        lines.append(f"用戶提到：")
        for msg in user_msgs[:3]:
            content = msg.get('content', '')[:100]
            timestamp = msg.get('timestamp', '')[:19]
            lines.append(f"  • [{timestamp}] {content}...")
        lines.append("")
    
    if assistant_msgs:
        lines.append(f"助手的回覆：")
        for msg in assistant_msgs[:3]:
            content = msg.get('content', '')[:100]
            timestamp = msg.get('timestamp', '')[:19]
            lines.append(f"  • [{timestamp}] {content}...")
    
    lines.append("")
    lines.append("提示：這是簡化的摘要，如需完整分析請稍後再試。")
    
    return "\n".join(lines)


def format_fallback_response(results: List[Dict[str, Any]], error: str) -> Dict[str, Any]:
    """
    Layer 3 Fallback: Format raw results as a fallback response.
    """
    if not results:
        return {
            "summary": "找不到相關的對話記錄。",
            "references": [],
            "fallback": True,
            "fallback_reason": error,
            "query": None
        }
    
    # Build simple summary from results
    summary_parts = [f"找到 {len(results)} 條相關記錄："]
    
    for i, r in enumerate(results[:5]):
        sender = r.get('sender', 'unknown')
        content = r.get('content', '')[:150]
        timestamp = r.get('timestamp', '')[:19]
        summary_parts.append(f"\n[{i+1}] [{timestamp}] {sender}: {content}...")
    
    return {
        "summary": "".join(summary_parts),
        "references": [
            {
                "content": r.get('content', '')[:200] + "...",
                "timestamp": r.get('timestamp', ''),
                "sender": r.get('sender', ''),
                "channel": r.get('channel', '')
            }
            for r in results[:5]
        ],
        "fallback": True,
        "fallback_reason": error,
        "query": results[0].get('query') if results else None,
        "total_found": len(results)
    }


def with_error_handling(func):
    """
    Decorator to apply three-layer error handling to a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_error = None
        
        for attempt in range(MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            
            except RateLimitError as e:
                last_error = e
                logger.warning(f"Rate limit hit, attempt {attempt + 1}/{MAX_RETRIES + 1}")
                if attempt < MAX_RETRIES:
                    time.sleep(RATE_LIMIT_WAIT)
                continue
            
            except (APITimeoutError, APIServerError) as e:
                last_error = e
                logger.warning(f"{type(e).__name__}, attempt {attempt + 1}/{MAX_RETRIES + 1}")
                if attempt < MAX_RETRIES:
                    time.sleep(SERVER_ERROR_WAIT)
                continue
            
            except NetworkError as e:
                last_error = e
                logger.error(f"Network error: {e}")
                break  # Don't retry network errors
            
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {type(e).__name__}: {e}")
                break
        
        # All retries failed, return fallback
        logger.error(f"All retries exhausted. Error: {last_error}")
        raise last_error
    
    return wrapper


def categorize_error(error: Exception) -> str:
    """
    Categorize an error for appropriate handling.
    """
    error_str = str(error).lower()
    
    if "429" in error_str or "rate" in error_str or "limit" in error_str:
        return "rate_limit"
    elif "timeout" in error_str or "timed out" in error_str:
        return "timeout"
    elif "500" in error_str or "502" in error_str or "503" in error_str or "server error" in error_str:
        return "server_error"
    elif "401" in error_str or "403" in error_str or "unauthorized" in error_str:
        return "auth_error"
    elif "connection" in error_str or "network" in error_str or "refused" in error_str:
        return "network_error"
    else:
        return "unknown_error"
