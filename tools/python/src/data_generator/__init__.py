"""
data_generator
==============

Reusable, secure generation engine for producing scenario-specific synthetic
datasets with Azure OpenAI and the Microsoft Agent Framework.
"""

from .engine import DataGenerator  # noqa: F401  (re-export)
from .tool import DataGeneratorTool  # noqa: F401  (re-export)

# Import the tools package for its side-effect: importing it registers every
# concrete DataGeneratorTool subclass in the registry used by ``from_name``.
from . import tools  # noqa: F401

__all__: list[str] = ["DataGenerator", "DataGeneratorTool"]
