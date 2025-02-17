import logging
import sys
import time
from dataclasses import dataclass

from kubernetes import client, config
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

log = logging.getLogger("kocker")
log.setLevel("DEBUG")
formatter = logging.Formatter("%(levelname)s:\t%(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)


@dataclass(frozen=True)
class RunOptions:
    image: str
    command: list[str]

    def __hash__(self):
        _hash = hash(
            (
                self.image,
                tuple(self.command),  # Make hashable
                time.time(),  # Add timestamp
            )
        )
        _hash += sys.maxsize + 1  # Ensure always positive
        return _hash


@dataclass(frozen=True)
class DeleteOptions:
    name: str


class Backend:
    def __init__(self):
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

    def run(self, options: RunOptions, rm=True) -> str:
        unique_pod_name = f"kocker-run-{hash(options)}"
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
                print(exec_resp.read_stdout())
            if exec_resp.peek_stderr():
                print(exec_resp.read_stderr())
        log.debug("Execution complete")
        exec_resp.close()

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
