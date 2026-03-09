from typing import Dict

from .agent_tasks.plan_initializer import AgentPlanInitTaskConfigSelector
from .agent_tasks.plan_enhancer import AgentPlanEnhancingTaskConfigSelector
from .agent_tasks.enhance_classifier import AgentEnhanceClassifierTaskConfigSelector
from ......utils import BaseAgentTaskConfigSelector

PLANENH_MAIN_LOG_PATH = 'log/qa/kg_reasoner/medium/plan_enhancer/main'

SPENH_AGENTASKS_SELECTORS_MAPPING: Dict[str, BaseAgentTaskConfigSelector] = {
    'plan_initing': AgentPlanInitTaskConfigSelector,
    'enhance_classifier': AgentEnhanceClassifierTaskConfigSelector,
    'plan_enhancing': AgentPlanEnhancingTaskConfigSelector
}
