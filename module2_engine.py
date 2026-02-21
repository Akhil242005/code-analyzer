from typing import Dict, List, Any
class Module2Input:
    def __init__(self, entity_id: str, attributes: Dict[str, Any],
                 context: Dict[str, Any], meta: Dict[str, Any]):
        self.entity_id = entity_id
        self.attributes = attributes
        self.context = context
        self.meta = meta

class Module2Output:
    def __init__(self, score: float, band: str,
                 confidence: float, reasons: List[Dict[str, Any]]):
        self.score = score
        self.band = band
        self.confidence = confidence
        self.reasons = reasons

class Module2Engine:
    def __init__(self):
        self.base_score = 0.5

    def evaluate(self, input_data: Module2Input) -> Module2Output:
        score = self.base_score
        reasons = []

        score = self._apply_delay_history(
            score,
            input_data.attributes,
            input_data.context,
            reasons
        )

        score = self._apply_inconsistency(
            score,
            input_data.attributes,
            input_data.context,
            reasons
        )

        score = self._apply_reliability(
            score,
            input_data.attributes,
            input_data.context,
            reasons
        )




        confidence = self._calculate_confidence(input_data.meta)
        band = self._map_band(score)
        return Module2Output(
            score=round(score, 2),
            band=band,
            confidence=round(confidence, 2),
            reasons=reasons
        )
    
    def _calculate_confidence(self, meta: Dict[str, Any]) -> float:
        completeness = meta.get("completeness", 1.0)
        source_confidence = meta.get("source_confidence", 1.0)
        return (completeness + source_confidence) / 2

    def _map_band(self, score: float) -> str:
        if score < 0.4:
            return "low"
        elif score < 0.7:
            return "moderate"
        else:
            return "high"

    def _apply_delay_history(self, score: float,
                             attributes: Dict[str, Any],
                             context: Dict[str, Any],
                             reasons: list) -> float:

        delay_frequency = attributes.get("delay_frequency")
        delay_severity = attributes.get("delay_severity")

        if delay_frequency is None and delay_severity is None:
            return score

        penalty = 0.0

        if delay_frequency is not None:
            penalty += delay_frequency * 0.1

        if delay_severity is not None:
            penalty += delay_severity * 0.1

        priority = context.get("priority_level", "medium")

        if priority == "high":
            penalty *= 1.2
        elif priority == "low":
            penalty *= 0.8

        new_score = max(0.0, score - penalty)

        reasons.append({
            "code": "DELAY_HISTORY",
            "direction": "negative",
            "impact": round(-penalty, 3)
        })

        return new_score
    
    def _apply_inconsistency(self, score: float,
                             attributes: Dict[str, Any],
                             context: Dict[str, Any],
                             reasons: list) -> float:

        inconsistency_score = attributes.get("inconsistency_score")

        if inconsistency_score is None:
            return score

        penalty = inconsistency_score * 0.15

        priority = context.get("priority_level", "medium")

        if priority == "high":
            penalty *= 1.25
        elif priority == "low":
            penalty *= 0.9

        new_score = max(0.0, score - penalty)

        reasons.append({
            "code": "INCONSISTENCY",
            "direction": "negative",
            "impact": round(-penalty, 3)
        })

        return new_score
    
    def _apply_reliability(self, score: float,
                           attributes: Dict[str, Any],
                           context: Dict[str, Any],
                           reasons: list) -> float:

        reliability_score = attributes.get("reliability_score")

        if reliability_score is None:
            return score

        boost = reliability_score * 0.12

        priority = context.get("priority_level", "medium")

        if priority == "high":
            boost *= 1.15
        elif priority == "low":
            boost *= 0.9

        new_score = min(1.0, score + boost)

        reasons.append({
            "code": "RELIABILITY",
            "direction": "positive",
            "impact": round(boost, 3)
        })

        return new_score
    
def evaluate_entity(payload: dict) -> dict:
    input_data = Module2Input(
        entity_id=payload.get("entity_id"),
        attributes=payload.get("attributes", {}),
        context=payload.get("context", {}),
        meta=payload.get("meta", {})
    )

    engine = Module2Engine()
    output = engine.evaluate(input_data)

    return {
        "entity_id": input_data.entity_id,
        "final_score": output.score,
        "decision_band": output.band,
        "confidence": output.confidence,
        "reasons": output.reasons
    }


if __name__ == "__main__":
    engine = Module2Engine()

    test_cases = [
        {
            "name": "High priority, moderate delays",
            "input": Module2Input(
                entity_id="CASE_1",
                attributes={
                    "delay_frequency": 0.6,
                    "delay_severity": 0.4,
                    "inconsistency_score": 0.5,
                    "reliability_score": 0.8
                },
                context={
                    "priority_level": "high"
                },
                meta={
                    "completeness": 0.9,
                    "source_confidence": 0.8
                }
            )
        },
        {
            "name": "Low priority, same delays",
            "input": Module2Input(
                entity_id="CASE_2",
                attributes={
                    "delay_frequency": 0.6,
                    "delay_severity": 0.4
                },
                context={
                    "priority_level": "low"
                },
                meta={
                    "completeness": 0.9,
                    "source_confidence": 0.8
                }
            )
        },
        {
            "name": "No delays at all",
            "input": Module2Input(
                entity_id="CASE_3",
                attributes={},
                context={
                    "priority_level": "medium"
                },
                meta={
                    "completeness": 0.95,
                    "source_confidence": 0.9
                }
            )
        },
        {
            "name": "Extreme delays, medium priority",
            "input": Module2Input(
                entity_id="CASE_4",
                attributes={
                    "delay_frequency": 1.0,
                    "delay_severity": 1.0
                },
                context={
                    "priority_level": "medium"
                },
                meta={
                    "completeness": 0.85,
                    "source_confidence": 0.9
                }
            )
        }
    ]

    for case in test_cases:
        print("\n---", case["name"], "---")
        result = engine.evaluate(case["input"])
        print("Entity:", case["input"].entity_id)
        print("Final Score:", result.score)
        print("Decision Band:", result.band)
        print("Confidence:", result.confidence)
        print("Reasons:", result.reasons)
