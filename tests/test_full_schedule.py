"""
Full end-to-end test of scheduling functionality
"""
import time
from Orbit_core.intent.source_selector import SourceSelector
from Orbit_core.llm.router import LLMRouter
from Orbit_core.config.settings import Settings

# Initialize
settings = Settings()
llm = LLMRouter(settings)
selector = SourceSelector(llm, settings)

print("=" * 60)
print("TESTING: open notepad in 5 seconds")
print("=" * 60)
result = list(selector.process("open notepad in 5 seconds"))
print(f"Response: {result[0]}")
print("\nWaiting 6 seconds to see if it executes...")
time.sleep(6)
print("\n" + "=" * 60)

print("\nTEST COMPLETE!")
print("\nIf you saw 'Scheduled task executed! Opening notepad.' above,")
print("and notepad opened, then the scheduling is working perfectly!")
