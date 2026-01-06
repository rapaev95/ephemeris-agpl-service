"""Version and build information."""

import os
from typing import Dict, Any


def get_version_info() -> Dict[str, Any]:
    """
    Get version and build information.

    Returns:
        Dictionary with version info
    """
    return {
        "service": "ephemeris-agpl-service",
        "api_version": "v1",
        "git_commit": os.getenv("GIT_COMMIT", "unknown"),
        "build_tag": os.getenv("BUILD_TAG", "dev"),
        "build_time_utc": os.getenv("BUILD_TIME_UTC", "unknown"),
    }


def get_source_info() -> Dict[str, Any]:
    """
    Get source code information for AGPL compliance.

    Returns:
        Dictionary with source info (repo, tag, commit, license)
    """
    git_commit = os.getenv("GIT_COMMIT", "unknown")
    build_tag = os.getenv("BUILD_TAG", "dev")
    repo_url = os.getenv("GITHUB_REPO_URL", "https://github.com/rapaev95/ephemeris-agpl-service")

    return {
        "license": "AGPL-3.0",
        "repo": repo_url,
        "tag": build_tag,
        "commit": git_commit,
        "how_to_get_source": f"Open the repository link or use the tag/commit shown. Repository: {repo_url}, Tag: {build_tag}, Commit: {git_commit}",
    }


def get_source_header() -> str:
    """
    Get X-AGPL-Source header value.

    Returns:
        Header value in format: <repo>@<tag-or-commit>
    """
    repo_url = os.getenv("GITHUB_REPO_URL", "https://github.com/rapaev95/ephemeris-agpl-service")
    build_tag = os.getenv("BUILD_TAG", "dev")
    git_commit = os.getenv("GIT_COMMIT", "unknown")

    # Use tag if available, otherwise commit
    version = build_tag if build_tag != "dev" else git_commit
    return f"{repo_url}@{version}"
