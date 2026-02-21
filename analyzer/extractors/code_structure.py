import os
import math


class CodeStructureExtractor:
    SOURCE_EXTENSIONS = {
        ".py", ".js", ".ts", ".java", ".cpp",
        ".c", ".cs", ".go", ".rs", ".php"
    }

    def __init__(self, repo_path, debug=False):
        self.repo_path = repo_path
        self.debug = debug

    def extract(self):
        file_line_counts = []

        for root, _, files in os.walk(self.repo_path):
            if ".git" in root:
                continue

            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in self.SOURCE_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    lines = self._count_lines(file_path)
                    if lines > 0:
                        file_line_counts.append(lines)

        if not file_line_counts:
            return {"inconsistency_score": 0.0}

        total_lines = sum(file_line_counts)
        file_count = len(file_line_counts)
        largest_file = max(file_line_counts)

        largest_ratio = largest_file / total_lines
        dominance_score = self._clamp((largest_ratio - 0.35) / 0.5, 0, 1)

        gini_score = self._gini(file_line_counts)

        expected_files = math.sqrt(total_lines)
        structure_ratio = file_count / expected_files if expected_files > 0 else 1
        structure_deficiency = self._clamp(1 - structure_ratio, 0, 1)

        inconsistency_score = (
            0.5 * dominance_score +
            0.3 * gini_score +
            0.2 * structure_deficiency
        )

        result = {
            "inconsistency_score": round(self._clamp(inconsistency_score, 0, 1), 3)
        }

        if self.debug:
            result["structure_debug"] = {
                "total_lines": total_lines,
                "file_count": file_count,
                "largest_ratio": round(largest_ratio, 3),
                "dominance_score": round(dominance_score, 3),
                "gini_score": round(gini_score, 3),
                "structure_deficiency": round(structure_deficiency, 3),
                "expected_files_sqrt": round(expected_files, 3)
            }

        return result

    def _count_lines(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0

    def _gini(self, values):
        sorted_vals = sorted(values)
        n = len(values)
        cumulative = 0
        for i, val in enumerate(sorted_vals, start=1):
            cumulative += i * val
        total = sum(sorted_vals)
        if total == 0:
            return 0
        gini = (2 * cumulative) / (n * total) - (n + 1) / n
        return self._clamp(gini, 0, 1)

    def _clamp(self, value, min_val, max_val):
        return max(min_val, min(value, max_val))