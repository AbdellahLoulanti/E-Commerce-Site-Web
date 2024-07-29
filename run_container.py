import socket
import subprocess
import json

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def run_container(port):
    command = f"docker run -d --name ansible-container-{port} -p {port}:5000 ansible-img"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode().strip()

def get_running_containers():
    command = "docker ps --format '{{json .}}'"
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    containers = result.stdout.decode().strip().split('\n')
    return [json.loads(container) for container in containers]

def main():
    used_ports = set()
    for container in get_running_containers():
        ports = container.get('Ports', '')
        if ports:
            port = int(ports.split('->')[0].split(':')[1])
            used_ports.add(port)

    port = find_free_port()
    while port in used_ports:
        port = find_free_port()
    
    print(f"Found available port: {port}")
    container_id = run_container(port)
    print(f"Container {container_id} is running on port {port}")

if __name__ == "__main__":
    main()
