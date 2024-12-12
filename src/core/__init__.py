"""Core functionality for browser automation and behavior simulation."""

from .browser import BrowserManager
from .fingerprint import generate_fingerprint, inject_fingerprint, FingerprintGenerator
from .human_behavior import HumanBehavior

__all__ = [
    'BrowserManager',
    'generate_fingerprint',
    'inject_fingerprint',
    'FingerprintGenerator',
    'HumanBehavior',
]