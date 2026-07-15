from src.dashboard.app import display_page

def test_display_page_routing_functionality():
    """Verify that display_page returns components containing expected titles."""
    
    # Test Employees page
    employees_page = display_page('/employees')
    # Use str(employees_page) to check for content (like headers)
    assert "Employees Overview" in str(employees_page)
    
    # Test Telemetry page
    telemetry_page = display_page('/telemetry')
    assert "Telemetry Analytics" in str(telemetry_page)
    
    # Test AI Report page
    ai_page = display_page('/ai-report')
    assert "AI Insights Report" in str(ai_page)
