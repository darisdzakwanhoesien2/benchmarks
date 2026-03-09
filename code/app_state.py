class AppState(dict):
    """Global shared application state (for cross-model access)."""
    pass

# Singleton instance for all modules to import
app_state = AppState()
