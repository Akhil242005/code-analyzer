import os
from analyzer.core.fetcher import RepoFetcher
from analyzer.core.signal_pipeline import SignalPipeline
from module2_engine import Module2Engine, Module2Input


REPO_NAME = "intro-to-git-github-Akhil242005"
CLONE_URL = "https://github.com/Akhil242005/intro-to-git-github-Akhil242005.git"
COMMIT_SHA = None


GITHUB_PAT = os.getenv("GITHUB_PAT")

if not GITHUB_PAT:
    raise ValueError("GITHUB_PAT environment variable not set")


fetcher = RepoFetcher(GITHUB_PAT)
path = fetcher.fetch(REPO_NAME, CLONE_URL, COMMIT_SHA)

print("Repository fetched at:", path)


pipeline = SignalPipeline(path)
signal_output = pipeline.run()

print("Extracted Signals:", signal_output)


engine = Module2Engine()

module_input = Module2Input(
    entity_id="LOCAL_TEST",
    attributes=signal_output["attributes"],
    context={"priority_level": "medium"},
    meta={"completeness": 1.0, "source_confidence": 1.0}
)

result = engine.evaluate(module_input)

print("\nFinal Score:", result.score)
print("Band:", result.band)
print("Confidence:", result.confidence)
print("Reasons:", result.reasons)