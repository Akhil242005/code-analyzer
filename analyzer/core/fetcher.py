import os
from git import Repo, GitCommandError


class RepoFetcher:
    def __init__(self, github_token: str, base_dir: str = "./repos"):
        if not github_token:
            raise ValueError("GitHub token (PAT) is required")

        self.github_token = github_token
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _auth_clone_url(self, clone_url: str) -> str:
        if clone_url.startswith("https://"):
            return clone_url.replace(
                "https://",
                f"https://{self.github_token}@"
            )
        raise ValueError("Only HTTPS clone URLs are supported")

    def fetch(self, repo_name: str, clone_url: str, commit_sha: str) -> str:
        """
        Clone repo and checkout specific commit.
        Reuse local repo if it already exists.
        Returns local repo path.
        """
        local_path = os.path.join(self.base_dir, repo_name.replace("/", "_"))

        try:
            if os.path.exists(local_path):
                repo = Repo(local_path)
                repo.git.fetch()
            else:
                auth_url = self._auth_clone_url(clone_url)
                repo = Repo.clone_from(auth_url, local_path)

            repo.git.checkout(commit_sha)
            return local_path

        except GitCommandError as e:
            raise RuntimeError(f"Git operation failed: {e}")
