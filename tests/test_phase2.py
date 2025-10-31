"""
Test Phase 2 Device Control Features
"""
from Orbit_core.actions.advanced_desktop import AdvancedDesktopControl
from Orbit_core.config.settings import Settings

# Initialize with phase2 config
settings = Settings("phase2_config.json")
advanced = AdvancedDesktopControl(settings)

print("=" * 60)
print("PHASE 2: DEVICE CONTROL - Feature Tests")
print("=" * 60)

# Test 1: Feature availability
print("\n1. Feature Status:")
print(f"   Screenshots: {'✅ Enabled' if advanced.enable_screenshots else '❌ Disabled'}")
print(f"   Recording: {'✅ Enabled' if advanced.enable_recording else '❌ Disabled'}")
print(f"   File Ops: {'✅ Enabled' if advanced.enable_file_ops else '❌ Disabled'}")
print(f"   Automation: {'✅ Enabled' if advanced.enable_automation else '❌ Disabled'}")
print(f"   Windows: {'✅ Enabled' if advanced.enable_window_mgmt else '❌ Disabled'}")

# Test 2: Configuration
print("\n2. Configuration:")
print(f"   Screenshot Dir: {advanced.screenshot_dir}")
print(f"   Recording Dir: {advanced.recording_dir}")
print(f"   Allowed Dirs: {len(advanced.allowed_dirs)} directories")
print(f"   File Categories: {len(advanced.file_categories)} categories")
print(f"   Macros: {len(advanced.macros)} predefined")

# Test 3: Command routing
print("\n3. Command Routing Test:")
test_commands = [
    "take screenshot",
    "record screen",
    "organize downloads",
    "list windows",
    "run macro morning_routine"
]

for cmd in test_commands:
    result = advanced.execute(cmd)
    print(f"   '{cmd}' → {result[:60]}...")

# Test 4: Help message
print("\n4. Help Message:")
help_msg = advanced._help_message()
print(help_msg)

print("\n" + "=" * 60)
print("PHASE 2 Test Complete!")
print("=" * 60)
