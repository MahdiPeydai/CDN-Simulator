from app.node import ServerNode, ClientNode


def register_server_nodes(servers: dict):
    server_a = ServerNode(name="A", database={}, latency=0, is_up=True)
    server_b = ServerNode(name="B", database={}, latency=0, is_up=True)
    server_c = ServerNode(name="C", database={}, latency=0, is_up=True)
    server_d = ServerNode(name="D", database={}, latency=0, is_up=True)
    server_e = ServerNode(name="E", database={}, latency=0, is_up=True)

    server_a.set_edge("B", 500)
    server_a.set_edge("C", 800)
    server_a.set_edge("D", 200)

    server_b.set_edge("A", 500)

    server_c.set_edge("A", 800)

    server_d.set_edge("A", 200)
    server_d.set_edge("E", 300)

    server_e.set_edge("D", 300)

    servers.update({
        "A": server_a,
        "B": server_b,
        "C": server_c,
        "D": server_d,
        "E": server_e,
    })


def register_client_nodes(clients: dict):
    client_0 = ClientNode(name="0")
    client_1 = ClientNode(name="1")

    client_0.set_edge("B", 200)
    client_0.set_edge("D", 100)
    client_0.set_edge("E", 150)

    client_1.set_edge("C", 50)
    client_1.set_edge("D", 700)

    clients.update({
        "0": client_0,
        "1": client_1,
    })