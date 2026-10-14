from analyzer import analyze_contract, extract_entities


def test_risk_flag_is_detected():
    result = analyze_contract("This agreement will automatically renew for one year.")
    assert result["risk_score"] > 0
    assert any(flag["category"] == "Automatic renewal" for flag in result["risk_flags"])


def test_entities_are_extracted():
    entities = extract_entities("Signed on January 4, 2026. Fee: $1,200. Email: legal@example.com")
    assert "January 4, 2026" in entities["dates"]
    assert "$1,200" in entities["monetary_values"]
    assert "legal@example.com" in entities["emails"]
