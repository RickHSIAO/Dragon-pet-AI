import os


os.environ.setdefault("DB_PATH", "sqlite:///:memory:")
# Unit tests must not read or write the developer's runtime provider settings.
# Persistence-specific tests instantiate ProviderSettingsService with temp paths.
os.environ.setdefault("SETTINGS_FILE_PATH", "")
