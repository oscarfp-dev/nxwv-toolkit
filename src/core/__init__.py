"""Shared primitives for declarative tools."""

from .http import BasicAuth, BearerAuth, HttpClient
from .tool import HttpTool

__all__ = ["BasicAuth", "BearerAuth", "HttpClient", "HttpTool"]
