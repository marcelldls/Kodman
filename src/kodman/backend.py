import io
import logging
import sys
import tarfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from kubernetes import client, config
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

log = logging.getLogger("kodman")


@dataclass(frozen=True)
class RunOptions:
    image: str
    command: list[str]
    volumes: list[str] = field(default_factory=lambda: [])

    def __hash__(self):
        hash_candidates = (
            self.image,
            self.command,
            self.volumes,
            time.time(),  # Add timestamp
        )

        to_hash = []
        for item in hash_candidates:
            if not item:  # Skip unhashable falsy items
                pass
            elif type(item) is list:  # Make hashable
                to_hash.append(tuple(item))
            else:
                to_hash.append(item)

        _hash = hash(tuple(to_hash))
        _hash += sys.maxsize + 1  # Ensure always positive
        return _hash


@dataclass(frozen=True)
class DeleteOptions:
    name: str


def cp_k8s(
    kube_conn: client.CoreV1Api,
    namespace: str,
    pod_name: str,
    source_path: Path,
    dest_path: Path,
):
    buf = io.BytesIO()
    if not source_path.is_dir() and dest_path.is_dir():
        arcname = dest_path.joinpath(source_path.name)
    else:
        arcname = dest_path

    with tarfile.open(fileobj=buf, mode="w:tar") as tar:
        tar.add(source_path, arcname=arcname)
    commands = [buf.getvalue()]

    # Copying file
    exec_command = ["tar", "xvf", "-", "-C", "/"]
    resp = stream(
        kube_conn.connect_get_namespaced_pod_exec,
        pod_name,
        namespace,
        command=exec_command,
        stderr=True,
        stdin=True,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    while resp.is_open():
        resp.update(timeout=1)
        if resp.peek_stdout():
            print(f"STDOUT: {resp.read_stdout()}")
        if resp.peek_stderr():
            print(f"STDERR: {resp.read_stderr()}")
        if commands:
            c = commands.pop(0)
            resp.write_stdin(c)
        else:
            break
    resp.close()


class Backend:
    def __init__(self):
        self.return_code = 0

    def connect(self):
        # Load config for user/serviceaccount https://github.com/kubernetes-client/python/issues/1005
        try:
            log.debug(
                "Loading kube config for user interaction from outside of cluster"
            )
            config.load_kube_config()
            log.debug("Loaded kube config successfully")
        except config.config_exception.ConfigException:
            log.debug("Failed to load kube config, trying in-cluster config")
            config.load_incluster_config()
            log.debug("Loaded in-cluster config successfully")

        self._client = client.CoreV1Api()
        self._context = config.list_kube_config_contexts()[1]["context"]
        log.debug("The current context is:")
        log.debug(f"  Cluster: {self._context['cluster']}")
        log.debug(f"  Namespace: {self._context['namespace']}")
        log.debug(f"  User: {self._context['user']}")

    def run(self, options: RunOptions) -> str:
        unique_pod_name = f"kodman-run-{hash(options)}"
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": unique_pod_name,
            },
            "spec": {
                "containers": [
                    {
                        "image": options.image,
                        "name": "container-name",
                        "command": ["/bin/sh"],
                        "args": [
                            "-c",
                            # Trap allows to kill the container gracefully
                            "trap 'exit 0' SIGTERM; while true;do date;sleep 1; done",
                        ],
                    }
                ]
            },
        }

        log.debug(f"Creating pod: {unique_pod_name}")
        self._client.create_namespaced_pod(
            body=pod_manifest, namespace=self._context["namespace"]
        )
        while True:
            read_resp = self._client.read_namespaced_pod(
                name=unique_pod_name, namespace=self._context["namespace"]
            )
            # Runtime type checking
            if isinstance(read_resp, V1Pod):
                if not read_resp.status:
                    raise ValueError("Empty pod status")
                elif read_resp.status.phase != "Pending":
                    log.debug("Pod status is 'Pending' (Accepted by the K8s system)")
                    break
                time.sleep(1)
            else:
                raise TypeError("Unexpected response type")

        # Mount volumes
        if options.volumes:
            for volume in options.volumes:
                process = volume.split(":")
                src = Path(process[0]).resolve()
                try:
                    dst = Path(process[1])
                except IndexError:
                    dst = src
                if not dst.is_absolute():
                    raise ValueError("Destination path must be absolute")
                log.debug(f"Transfer {src} to {dst}")
                cp_k8s(
                    self._client,
                    self._context["namespace"],
                    unique_pod_name,
                    src,
                    dst,
                )

        # Calling exec interactively
        log.debug("Execution start")
        exec_resp = stream(
            self._client.connect_get_namespaced_pod_exec,
            unique_pod_name,
            self._context["namespace"],
            command=options.command,
            stderr=True,
            stdin=True,
            stdout=True,
            tty=False,
            _preload_content=False,
        )

        while exec_resp.is_open():
            exec_resp.update(timeout=5)
            if exec_resp.peek_stdout():
                print(exec_resp.read_stdout().rstrip())
            if exec_resp.peek_stderr():
                print(exec_resp.read_stderr().rstrip())
        log.debug("Execution complete")
        exec_resp.close()
        self.return_code = exec_resp.returncode

        return unique_pod_name

    def delete(self, options: DeleteOptions):
        try:
            exists_resp = self._client.read_namespaced_pod(
                name=options.name,
                namespace=self._context["namespace"],
            )
            self._client.delete_namespaced_pod(
                name=options.name,
                namespace=self._context["namespace"],
                grace_period_seconds=2,  # Is this too aggressive?
            )
            log.debug("Awaiting pod cleanup...")
            while exists_resp:
                try:
                    exists_resp = self._client.read_namespaced_pod(
                        name=options.name,
                        namespace=self._context["namespace"],
                    )
                    time.sleep(2)
                except ApiException as e:
                    if e.status == 404:
                        log.debug(f"Pod {options.name} deleted successfully")
                        break
                    else:
                        raise e

        except ApiException as e:
            log.debug(f"Error deleting pod: {e}")
