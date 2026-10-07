from app import app

def test_home_page():
  app.config["TESTING"] = True

  with app.test_config() as client:
    response =  client.get("/")

    assert response.status_code = 200
