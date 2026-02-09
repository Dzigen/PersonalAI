import dspy

EVAL_JUDGE_MAIN_LOG_PATH = 'log/kg_eval/mine/judge'

DEFAULT_LLM_GENSTRATEGY = {"num_predict": 2048, "seed": 42, "top_k": 1, "temperature": 0.0}

# Define DSPy signature for evaluation
class EvaluateResponse(dspy.Signature):
    """Determine whether the context contains the information stated in the correct answer. Respond with 1 if yes, 0 if no."""

    context: str = dspy.InputField(desc="The context to evaluate")
    correct_answer: str = dspy.InputField(desc="The correct answer to check for")
    evaluation: int = dspy.OutputField(
        desc="1 if context contains the correct answer, 0 otherwise"
    )


# Create DSPy module for evaluation
class ResponseEvaluator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.evaluate = dspy.ChainOfThought(EvaluateResponse)

    def forward(self, context, correct_answer):
        return self.evaluate(context=context, correct_answer=correct_answer)
