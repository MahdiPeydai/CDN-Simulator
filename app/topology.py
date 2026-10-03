from app.domain.node import ClientNode, ServerNode


def create_servers() -> dict[str, ServerNode]:
    servers = {
        name: ServerNode(name)
        for name in ["A", "B", "C", "D", "E"]
    }

    servers["A"].add_edge("B", 500)
    servers["A"].add_edge("C", 800)
    servers["A"].add_edge("D", 200)

    servers["B"].add_edge("A", 500)

    servers["C"].add_edge("A", 800)

    servers["D"].add_edge("A", 200)
    servers["D"].add_edge("E", 300)

    servers["E"].add_edge("D", 300)

    return servers


def create_clients() -> dict[str, ClientNode]:
    clients = {
        name: ClientNode(name)
        for name in ["0", "1"]
    }

    clients["0"].add_edge("B", 200)
    clients["0"].add_edge("D", 100)
    clients["0"].add_edge("E", 150)

    clients["1"].add_edge("C", 50)
    clients["1"].add_edge("D", 700)

    return clients


def create_topology() -> tuple[dict[str, ServerNode], dict[str, ClientNode]]:
    servers = create_servers()
    clients = create_clients()

    return servers, clients