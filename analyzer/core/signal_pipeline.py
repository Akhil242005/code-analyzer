from analyzer.extractors.commit_evolution import CommitEvolutionExtractor
from analyzer.extractors.code_structure import CodeStructureExtractor


class SignalPipeline:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.extractors = [
            CommitEvolutionExtractor(repo_path),
            CodeStructureExtractor(repo_path)
        ]

    def run(self):
        attributes = {}
        meta = {}

        for extractor in self.extractors:
            result = extractor.extract()
            if isinstance(result, dict):
                for key, value in result.items():
                    attributes[key] = value

        return {
            "attributes": attributes,
            "meta": meta
        }