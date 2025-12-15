from dataclasses import dataclass, fields
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class Question:
    question: str
    answer: str
    evidence: list[str]
    category: str
    rephrased_question: str
    was_reject_while_rephrasing: bool = False
    raw_answer: str = Optional[None]
    final_answer : str = Optional[None]


    @classmethod
    def from_dict(cls, data: Dict[str, Any]):

        return cls(
            question=data["question"],
            answer=data["answer"],
            evidence=data["evidence"],
            category=data["category"],
            rephrased_question=data.get("rephrased_question"),
            was_reject_while_rephrasing=data.get("was_reject_while_rephrasing", False),
            raw_answer=data.get("raw_answer"),
            final_answer=data.get("final_answer")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "evidence": self.evidence,
            "category": self.category,
            "rephrased_question": self.rephrased_question,
            "was_reject_while_rephrasing": self.was_reject_while_rephrasing,
            "raw_answer": self.raw_answer,
            "final_answer": self.final_answer
        }