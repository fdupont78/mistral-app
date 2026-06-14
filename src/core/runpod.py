"""
RunPod API Client

Wrapper for the RunPod REST API.
API Documentation: https://docs.runpod.io/api-reference/pods/POST/pods
"""

from typing import Any

import requests

RUNPOD_REST_API_URL = "https://rest.runpod.io/v1"


class RunPodClient:
    """Client for interacting with the RunPod REST API."""

    def __init__(self, api_key: str):
        """
        Initialize the RunPod client.

        Args:
            api_key: RunPod API key
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def create_pod(
        self,
        template_id: str,
        env_vars: dict[str, str],
        name: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new pod on RunPod using a template.

        Args:
            template_id: RunPod template ID (e.g., 'hsrb8il0fj')
            env_vars: Environment variables to set in the pod
            name: Optional name for the pod

        Returns:
            Pod information including id, machineId, and publicIp
        """
        branch = env_vars.get("GITHUB_BRANCH", "master")

        payload = {
            "templateId": template_id,
            "name": name or f"mistral-app-{branch}",
            "gpuTypeIds": ["NVIDIA A40"],
            "cloudType": "SECURE",
            "computeType": "GPU",
            "env": env_vars,
            "ports": ["8501/http","8888/http", "22/tcp"],
        }

        response = requests.post(
            f"{RUNPOD_REST_API_URL}/pods",
            json=payload,
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_pod(self, pod_id: str) -> dict[str, Any]:
        """
        Get information about a pod.

        Args:
            pod_id: The pod ID

        Returns:
            Pod information including status, machineId, and portMappings
        """
        response = requests.get(
            f"{RUNPOD_REST_API_URL}/pods/{pod_id}",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_pod_status(self, pod_id: str) -> str:
        """
        Get the status of a pod.

        Args:
            pod_id: The pod ID

        Returns:
            Pod status (e.g., 'RUNNING', 'PENDING', 'STOPPED')
        """
        pod_info = self.get_pod(pod_id)
        return pod_info.get("desiredStatus", pod_info.get("status", "UNKNOWN"))

    def stop_pod(self, pod_id: str) -> dict[str, Any]:
        """
        Stop a running pod.

        Args:
            pod_id: The pod ID

        Returns:
            Pod information after stopping
        """
        response = requests.post(
            f"{RUNPOD_REST_API_URL}/pods/{pod_id}/stop",
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_streamlit_url(self, pod_id: str) -> str:
        """
        Get the Streamlit URL for a pod.

        Args:
            pod_id: The pod ID

        Returns:
            Streamlit URL (e.g., https://<pod_id>-8501.proxy.runpod.net)
        """
        return f"https://{pod_id}-8501.proxy.runpod.net"
