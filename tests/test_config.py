import os
print("Environment variables:")
for key, value in os.environ.items():
    if key.startswith("ORBIT_"):
        print(f"  {key} = {value}")

from Orbit_core.config.settings import Settings
settings = Settings()
print(f"\nSettings:")
print(f"  OLLAMA_MODEL = {settings.OLLAMA_MODEL}")
print(f"  _get_config result = {settings._get_config('ollama_model', 'DEFAULT')}")