"""
Internationalization (i18n) Support
Multilingual support for SQL Analyzer Enterprise
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class Language(Enum):
    """Supported languages."""
    SPANISH = "es"
    ENGLISH = "en"
    PORTUGUESE = "pt"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"


class I18nManager:
    """Internationalization manager."""
    
    def __init__(self, default_language: Language = Language.SPANISH):
        self.default_language = default_language
        self.current_language = default_language
        self.translations: Dict[str, Dict[str, str]] = {}
        self.fallback_translations: Dict[str, str] = {}
        
        # Load translations
        self._load_translations()
    
    def set_language(self, language: Language):
        """Set the current language."""
        self.current_language = language
    
    def get_language(self) -> Language:
        """Get the current language."""
        return self.current_language
    
    def translate(self, key: str, language: Optional[Language] = None, **kwargs) -> str:
        """Translate a key to the specified or current language."""
        target_language = language or self.current_language
        
        # Get translation
        translations = self.translations.get(target_language.value, {})
        translated = translations.get(key)
        
        # Fallback to default language if not found
        if translated is None:
            translated = self.fallback_translations.get(key, key)
        
        # Format with kwargs if provided
        if kwargs:
            try:
                translated = translated.format(**kwargs)
            except (KeyError, ValueError):
                # If formatting fails, return the unformatted string
                pass
        
        return translated
    
    def t(self, key: str, **kwargs) -> str:
        """Shorthand for translate."""
        return self.translate(key, **kwargs)
    
    def get_available_languages(self) -> List[Language]:
        """Get list of available languages."""
        return [Language(lang) for lang in self.translations.keys()]
    
    def get_language_name(self, language: Language) -> str:
        """Get the native name of a language."""
        names = {
            Language.SPANISH: "Español",
            Language.ENGLISH: "English",
            Language.PORTUGUESE: "Português",
            Language.FRENCH: "Français",
            Language.GERMAN: "Deutsch",
            Language.ITALIAN: "Italiano"
        }
        return names.get(language, language.value)


# Global i18n manager instance
_i18n_manager: Optional[I18nManager] = None


def get_i18n_manager() -> I18nManager:
    """Get the global i18n manager instance."""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def set_language(language: Language):
    """Set the global language."""
    get_i18n_manager().set_language(language)


def translate(key: str, **kwargs) -> str:
    """Translate a key using the global i18n manager."""
    return get_i18n_manager().translate(key, **kwargs)


def t(key: str, **kwargs) -> str:
    """Shorthand for translate using the global i18n manager."""
    return translate(key, **kwargs)


# Convenience functions for common translations
def get_error_severity_text(severity: str) -> str:
    """Get localized text for error severity."""
    severity_map = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low"
    }
    return translate(severity_map.get(severity.upper(), "medium"))


def get_status_text(status: str) -> str:
    """Get localized text for status."""
    status_map = {
        "processing": "processing",
        "completed": "completed",
        "failed": "failed",
        "loading": "loading",
        "connecting": "connecting",
        "connected": "connected",
        "disconnected": "disconnected"
    }
    return translate(status_map.get(status.lower(), status))


def format_time_ago(seconds: int) -> str:
    """Format time ago in localized format."""
    if seconds < 60:
        return translate("seconds_ago", seconds=seconds)
    elif seconds < 3600:
        minutes = seconds // 60
        return translate("minutes_ago", minutes=minutes)
    elif seconds < 86400:
        hours = seconds // 3600
        return translate("hours_ago", hours=hours)
    else:
        days = seconds // 86400
        return translate("days_ago", days=days)


def format_file_size(size_bytes: int) -> str:
    """Format file size in localized format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
