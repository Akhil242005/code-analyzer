from git import Repo
from datetime import datetime


class CommitEvolutionExtractor:
    def __init__(self, repo_path: str):
        self.repo = Repo(repo_path)

    def extract(self) -> dict:
        commits = list(self.repo.iter_commits())

        if not commits:
            return {
                "commit_count": 0,
                "avg_gap_hours": None,
                "reliability_score": 0.0
            }

        commit_times = [
            datetime.fromtimestamp(commit.committed_date)
            for commit in commits
        ]

        commit_times.sort()

        gaps = []
        for i in range(1, len(commit_times)):
            gap_hours = (
                (commit_times[i] - commit_times[i - 1]).total_seconds()
                / 3600
            )
            gaps.append(gap_hours)

        avg_gap = sum(gaps) / len(gaps) if gaps else None

        # Simple heuristic for pre-MVP
        if len(commits) >= 5:
            reliability = 0.8
        elif len(commits) >= 3:
            reliability = 0.6
        else:
            reliability = 0.3

        return {
            "commit_count": len(commits),
            "avg_gap_hours": avg_gap,
            "reliability_score": reliability
        }
