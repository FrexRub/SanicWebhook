async def test_index_route(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "* Transaction handler *" in response.text
