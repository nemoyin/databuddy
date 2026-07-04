from jwbuddy.data.schema import SchemaInspector


def test_schema_to_prompt():
    tables = [
        {
            "table": "users",
            "columns": [
                {"name": "id", "type": "integer", "nullable": False, "default": "", "comment": "主键"},
                {"name": "name", "type": "varchar", "nullable": True, "default": "", "comment": "姓名"},
            ],
        }
    ]
    prompt = SchemaInspector.schema_to_prompt(tables)
    assert "users" in prompt
    assert "主键" in prompt
    assert "varchar" in prompt
