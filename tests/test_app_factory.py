def test_app_factory_registers_blueprints(app):
    router_rules = {rule.endpoint for rule in app.url_map.iter_rules()}
    assert any(ep.startswith('main.') for ep in router_rules)
    assert any(ep.startswith('auth.') for ep in router_rules)
