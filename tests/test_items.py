def test_read_item(client):
    response = client.get("/items/42")
    assert response.status_code == 200
    body = response.json()
    assert body["item_id"] == 42
    assert body["db_queries"] == 1
