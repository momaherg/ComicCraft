"""
Comic Generation Package

This package provides AI-powered generation for comic creation:
- Character generation from photos, comic images, or text
- Location generation from photos or text
- Panel generation with character placement and backgrounds
"""

from .character_gen import CharacterGenerator
from .location_gen import LocationGenerator
from .panel_gen import PanelGenerator

__all__ = [
    'CharacterGenerator',
    'LocationGenerator',
    'PanelGenerator',
]

__version__ = '0.1.0'
