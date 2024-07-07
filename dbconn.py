from cassandra.cluster import Cluster

#подключение к ноде 1 или 2 в зависимости от досутпности
def get_cassandra_session():
    contact_points = ['127.0.0.1']
    ports = [9042, 9043]
    timeout = 0.05
    
    for port in ports:
        try:
            cluster = Cluster(contact_points, port=port, connect_timeout=timeout)
            session = cluster.connect('tweeter')
            print(f"[Warning!] Active Port: {port}")
            return session
        except Exception as e:
            print(f"[Warning!] Failed to connect:{port}")
    raise Exception("Could not connect to any Cassandra nodes.")
