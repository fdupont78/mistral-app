"""
RunPod Deployment CLI Module

Handles deployment to RunPod via REST API.
"""

import os
import time

from src.core.runpod import RunPodClient


def deploy_to_runpod(
    branch: str = "master",
    api_key: str | None = None,
    template_id: str | None = None,
) -> str:
    """
    Deploy the Mistral App to RunPod.

    Args:
        branch: GitHub branch to deploy (default: master)
        api_key: RunPod API key (overrides RUNPOD_API_KEY env var)
        template_id: RunPod template ID (overrides RUNPOD_TEMPLATE_ID env var)

    Returns:
        Streamlit URL of the deployed pod

    Raises:
        ValueError: If RUNPOD_API_KEY is missing
        TimeoutError: If pod fails to start
    """
    api_key = api_key or os.getenv("RUNPOD_API_KEY")
    template_id = template_id or os.getenv("RUNPOD_TEMPLATE_ID", "hsrb8il0fj")

    if not api_key:
        raise ValueError(
            "RUNPOD_API_KEY required.\n"
            "Provide it via:\n"
            "  - Env var: export RUNPOD_API_KEY=xxx\n"
            "  - CLI arg: python -m src.main deploy --api-key xxx\n"
            "  - GitHub Secret: RUNPOD_API_KEY"
        )

    client = RunPodClient(api_key)

    print("🚀 Creating RunPod instance...")
    pod = client.create_pod(template_id, name=f"mistral-app-{branch}")
    pod_id = pod["id"]
    print(f"✅ Pod created: {pod_id}")

    print("⏳ Waiting for pod to start...")
    for _ in range(30):  # Wait up to 5 minutes
        status = client.get_pod_status(pod_id)
        if status == "RUNNING":
            break
        time.sleep(10)
    else:
        raise TimeoutError(f"Pod {pod_id} did not start in time. Status: {status}")

    streamlit_url = client.get_streamlit_url(pod_id)
    print("\n🎉 Application deployed!")
    print(f"🔗 URL: {streamlit_url}")
    return streamlit_url
