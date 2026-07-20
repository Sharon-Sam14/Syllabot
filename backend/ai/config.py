"""
backend/ai/config.py

Thin backward-compatibility shim.
All AI settings now live in backend.core.config.Settings.
This module re-exports `ai_settings` as an alias for the unified settings object
so that any existing imports of `ai_settings` continue to work without modification.
"""
from backend.core.config import settings

# Alias for backward compatibility — all existing code that imports
# `from backend.ai.config import ai_settings` will work unchanged.
ai_settings = settings
