import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from core.fetcher import RepoFetcher
from extractors.commit_evolution import CommitEvolutionExtractor
from module2_engine import evaluate_entity  # adjust if function name differs

if __name__ == "__main__":
    GITHUB_PAT = os.getenv("GITHUB_PAT")

    # TEMP test values — replace with a real repo
    REPO_NAME = "intro-to-git-github-Akhil242005"
    CLONE_URL = "https://github.com/CorrusOfficial/intro-to-git-github-Akhil242005"
    COMMIT_SHA = "main"

    fetcher = RepoFetcher(GITHUB_PAT)
    path = fetcher.fetch(REPO_NAME, CLONE_URL, COMMIT_SHA)

    print("Repository fetched at:", path)

    # Sanity checks
    print("Files in repo root:")
    print(os.listdir(path))

    extractor = CommitEvolutionExtractor(path)
    result = extractor.extract()

    print("\nCommit Evolution Analysis:")
    print(result)


module2_input = {
    "entity_id": REPO_NAME,
    "attributes": {
        "reliability_score": result["reliability_score"]
    },
    "context": {
        "priority_level": "medium"
    },
    "meta": {
        "source_confidence": 0.8
    }
}

decision = evaluate_entity(module2_input)

print("\nModule 2 Decision:")
print(decision)
