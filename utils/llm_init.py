"""Initialize ChatGoogleGenerativeAI to resolve Pydantic v2 forward references.

This module must be imported BEFORE any nodes that use ChatGoogleGenerativeAI
to ensure all forward references are properly resolved.
"""

# Step 1: Import BaseCache first (required by Pydantic v2 error message)
from langchain_core.caches import BaseCache

# Step 2: Import ChatGoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Step 3: Try to import all types that might be forward references
# Import them into this module's namespace so model_rebuild() can find them
try:
    # Callbacks is often a type alias, try importing from various locations
    from langchain_core.callbacks.base import Callbacks
except ImportError:
    try:
        from langchain_core.callbacks import Callbacks
    except ImportError:
        # Callbacks might not be directly importable - that's okay
        # We'll let model_rebuild() handle it
        pass

# Step 4: Call model_rebuild() at module level
# This is CRITICAL - it must be called after BaseCache is imported
# and it uses this module's globals() to resolve forward references
try:
    ChatGoogleGenerativeAI.model_rebuild()
except Exception as e:
    # If model_rebuild fails with a forward reference error, we need to fix it
    error_str = str(e)
    if "Callbacks" in error_str and "not defined" in error_str:
        # Callbacks forward reference can't be resolved
        # Try to work around by creating a dummy type in the namespace
        import typing
        if 'Callbacks' not in globals():
            # Create a type alias that Pydantic can use
            Callbacks = typing.Optional[typing.List[typing.Any]]
        # Try rebuilding again
        try:
            ChatGoogleGenerativeAI.model_rebuild()
        except Exception as e2:
            # Still failing - this is a critical error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to rebuild ChatGoogleGenerativeAI: {e2}")
            raise
    elif "not fully defined" in error_str:
        # This is the error we're trying to fix - must raise it
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"ChatGoogleGenerativeAI not fully defined: {e}")
        raise
    else:
        # Some other error - might be okay to continue
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"model_rebuild() warning: {e}")

