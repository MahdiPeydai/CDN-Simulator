from fastapi.testclient import TestClient

from app.main import fastapi_app, SERVERS



def test_docs_are_not_blocked_by_cdn_middleware():
    with TestClient(fastapi_app) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200


def test_request_requires_client_node_header():
    with TestClient(fastapi_app) as client:
        response = client.get("/data/key")
        assert response.status_code == 400
        assert response.json() == {'message': 'X-Client-IP not provided'}


def test_unknown_client_node_is_rejected():
    with TestClient(fastapi_app) as client:
        response = client.get("/data/key", headers={"X-Client-Node": "unknown"})
        assert response.status_code == 400
        assert response.json() == {"message": "Client node not found"}


def test_all_servers_up_scenario_data_found():
    with TestClient(fastapi_app) as client:
        for server in SERVERS.values():
            server.update_data("key", server.name)

        response0 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "0",
            },
        )
        assert response0.status_code == 200
        # user 0 nearest node is D so returned value is D
        assert response0.json() == {'result': 'D', 'success': True}
        duration = float(
            response0.headers["X-Simulation-Duration"]
        )
        print(duration)


        response1 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "1",
            },
        )
        assert response1.status_code == 200
        # user 1 nearest node is C so returned value is C
        assert response1.json() == {'result': 'C', 'success': True}
        duration = float(
            response1.headers["X-Simulation-Duration"]
        )
        print(duration)


def test_all_servers_up_scenario_data_not_found():
    with TestClient(fastapi_app) as client:
        for server in SERVERS.values():
            server.update_data("key", server.name)

        response0 = client.get(
            "/data/invalid",
            headers={
                "X-Client-Node": "0",
            },
        )
        assert response0.status_code == 404
        # user 0 nearest node is D so returned value is D
        assert response0.json() == {'result': None, 'success': False, 'message': 'data not found'}
        duration = float(
            response0.headers["X-Simulation-Duration"]
        )
        print(duration)


        response1 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "1",
            },
        )
        assert response1.status_code == 200
        # user 1 nearest node is C so returned value is C
        assert response1.json() == {'result': 'C', 'success': True}
        duration = float(
            response1.headers["X-Simulation-Duration"]
        )
        print(duration)


def test_only_server_a_has_data_scenario():
    with TestClient(fastapi_app) as client:
        SERVERS["A"].update_data("key", SERVERS["A"].name)

        response0 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "0",
            },
        )
        assert response0.status_code == 200
        # user 0 nearest node is D, but it must get data from server A
        assert response0.json() == {'result': 'A', 'success': True}
        # now server D must have data {"key": "A"}
        assert SERVERS["D"].get_data("key") == SERVERS["A"].name
        duration = float(
            response0.headers["X-Simulation-Duration"]
        )
        print(duration)


        response1 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "1",
            },
        )
        assert response1.status_code == 200
        # user 1 nearest node is C, but it must get data from server A
        assert response1.json() == {'result': 'A', 'success': True}
        # now server C must have data {"key": "A"}
        assert SERVERS["C"].get_data("key") == SERVERS["A"].name
        duration = float(
            response1.headers["X-Simulation-Duration"]
        )
        print(duration)


def test_server_c_down_scenario():
    with TestClient(fastapi_app) as client:

        for server in SERVERS.values():
            server.update_data("key", server.name)

        SERVERS["C"].mark_down()

        response1 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "1",
            },
        )
        assert response1.status_code == 200
        # user 1 nearest node is C, but it must get data from server D
        assert response1.json() == {'result': 'D', 'success': True}
        # server D min response is 70ms
        duration = float(
            response1.headers["X-Simulation-Duration"]
        )
        print(duration)
        assert duration >= 0.07


def test_server_d_busy_scenario():
    with TestClient(fastapi_app) as client:

        for server in SERVERS.values():
            server.update_data("key", server.name)

        SERVERS["D"].set_latency(200)

        response1 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "0",
            },
        )
        assert response1.status_code == 200
        # user 0 nearest node is C, but it must get data from server E as D is busy
        assert response1.json() == {'result': 'E', 'success': True}
        # server D min response is 70ms
        duration = float(
            response1.headers["X-Simulation-Duration"]
        )
        print(duration)
        assert duration >= 0.015


def test_propagation():
    with TestClient(fastapi_app) as client:
        for server in SERVERS.values():
            server.update_data("key", "test")

        response1 = client.post(
            "/data/key",
            json="test_new",
            headers={
                "X-Client-Node": "1",
            },
        )
        assert response1.status_code == 200
        assert response1.json() == {'result': 'test_new', 'success': True}
        # user 1 nearest node is C, so other servers must not have key data as they invalidate it
        for server in SERVERS.values():
            if server.name != "C":
                assert server.get_data("key") is None
        duration = float(
            response1.headers["X-Simulation-Duration"]
        )
        print(duration)

        # get updated data from other servers
        response0 = client.get(
            "/data/key",
            headers={
                "X-Client-Node": "0",
            },
        )
        assert response0.status_code == 200
        # user 0 nearest node is D, it is empty, but it must get it from c
        assert response0.json() == {'result': 'test_new', 'success': True}
        duration = float(
            response0.headers["X-Simulation-Duration"]
        )
        print(duration)
        # data get from c -> a -> d, so minimum response time is 110ms
        assert duration >= 0.11