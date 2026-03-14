from src.domain.enums import EventTypes
from src.domain.events import StepCompensated, StepCompleted, StepFailed

order_event_type_mapper = {
    EventTypes.STEP_COMPLETED: StepCompleted,
    EventTypes.STEP_COMPENSATED: StepCompensated,
    EventTypes.STEP_FAILED: StepFailed,
}


event_type_mapper = {
    StepCompleted.__name__: EventTypes.STEP_COMPLETED,
    StepCompensated.__name__: EventTypes.STEP_COMPENSATED,
    StepFailed.__name__: EventTypes.STEP_FAILED,
}
