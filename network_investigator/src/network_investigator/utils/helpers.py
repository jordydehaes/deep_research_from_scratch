"""Helper utilities for network investigator."""

from datetime import datetime, timezone
from typing import List
from rich.console import Console
from rich.panel import Panel

# Console for rich output
console = Console()

def get_current_time() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)

def format_messages_simple(messages: List) -> None:
    """Simple message formatting for testing."""
    for message in messages:
        if hasattr(message, 'content'):
            role = message.__class__.__name__.replace('Message', '').lower()
            console.print(Panel(
                str(message.content), 
                title=f"🤖 {role.title()}" if role == 'ai' else f"👤 {role.title()}"
            ))

def extract_device_names(text: str) -> List[str]:
    """Extract potential device names from text.
    
    This is a simple implementation - in production you'd have more sophisticated
    network device name parsing based on your naming conventions.
    """
    import re
    
    # Common network device patterns
    patterns = [
        r'\b[Rr]outer[s]?\s*([A-Za-z0-9-]+)',  # Router X, router-01
        r'\b[Ss]witch[es]?\s*([A-Za-z0-9-]+)', # Switch Y, switches-core
        r'\b([A-Za-z0-9-]+[-_][Rr]outer)',     # core-router
        r'\b([A-Za-z0-9-]+[-_][Ss]witch)',     # access-switch
        r'\b([A-Za-z0-9]+\-[0-9]+)',          # generic device-01
        r'\b([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', # IP addresses
    ]
    
    devices = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            device = match.group(1) if len(match.groups()) > 0 else match.group(0)
            if device and device.lower() not in ['router', 'switch', 'routers', 'switches']:
                devices.append(device.strip())
    
    return list(set(devices))  # Remove duplicates

def extract_time_references(text: str) -> List[str]:
    """Extract time references from text."""
    import re
    
    # Common time patterns  
    patterns = [
        r'\b(?:at|around|about|since|from|until)\s+([0-9]{1,2}:[0-9]{2}(?:\s*[AP]M)?)\b',
        r'\b([0-9]{1,2}\s*hours?\s*ago)\b',
        r'\b([0-9]{1,2}\s*minutes?\s*ago)\b', 
        r'\b(this\s+morning|this\s+afternoon|this\s+evening|yesterday|today)\b',
        r'\b([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})\b',
        r'\b([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\b',
        r'\b(last\s+hour|last\s+few\s+hours)\b'
    ]
    
    time_refs = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            time_ref = match.group(1) if len(match.groups()) > 0 else match.group(0)
            time_refs.append(time_ref.strip())
    
    return time_refs