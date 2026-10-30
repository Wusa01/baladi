def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Baladi" in response.get_data(as_text=True)


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["application"] == "Baladi"
