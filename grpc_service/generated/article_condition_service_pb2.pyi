from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ObservedCondition(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OBSERVED_CONDITION_UNSPECIFIED: _ClassVar[ObservedCondition]
    AS_NEW: _ClassVar[ObservedCondition]
    MINOR_WEAR: _ClassVar[ObservedCondition]
    VISIBLY_WORN: _ClassVar[ObservedCondition]
    DAMAGED: _ClassVar[ObservedCondition]
    MISSING_TAGS: _ClassVar[ObservedCondition]
    MISSING_PARTS: _ClassVar[ObservedCondition]

class Decision(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DECISION_UNSPECIFIED: _ClassVar[Decision]
    ACCEPT: _ClassVar[Decision]
    REJECT: _ClassVar[Decision]
    MANUAL_REVIEW: _ClassVar[Decision]
OBSERVED_CONDITION_UNSPECIFIED: ObservedCondition
AS_NEW: ObservedCondition
MINOR_WEAR: ObservedCondition
VISIBLY_WORN: ObservedCondition
DAMAGED: ObservedCondition
MISSING_TAGS: ObservedCondition
MISSING_PARTS: ObservedCondition
DECISION_UNSPECIFIED: Decision
ACCEPT: Decision
REJECT: Decision
MANUAL_REVIEW: Decision

class ConditionCheckRequest(_message.Message):
    __slots__ = ("return_id", "sku", "observed_condition", "image_urls", "tags_present", "original_packaging", "inspector_note", "inspected_at")
    RETURN_ID_FIELD_NUMBER: _ClassVar[int]
    SKU_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_CONDITION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URLS_FIELD_NUMBER: _ClassVar[int]
    TAGS_PRESENT_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_PACKAGING_FIELD_NUMBER: _ClassVar[int]
    INSPECTOR_NOTE_FIELD_NUMBER: _ClassVar[int]
    INSPECTED_AT_FIELD_NUMBER: _ClassVar[int]
    return_id: str
    sku: str
    observed_condition: ObservedCondition
    image_urls: _containers.RepeatedScalarFieldContainer[str]
    tags_present: bool
    original_packaging: bool
    inspector_note: str
    inspected_at: str
    def __init__(self, return_id: _Optional[str] = ..., sku: _Optional[str] = ..., observed_condition: _Optional[_Union[ObservedCondition, str]] = ..., image_urls: _Optional[_Iterable[str]] = ..., tags_present: _Optional[bool] = ..., original_packaging: _Optional[bool] = ..., inspector_note: _Optional[str] = ..., inspected_at: _Optional[str] = ...) -> None: ...

class ConditionCheckBatchRequest(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedCompositeFieldContainer[ConditionCheckRequest]
    def __init__(self, items: _Optional[_Iterable[_Union[ConditionCheckRequest, _Mapping]]] = ...) -> None: ...

class ConditionCheckBatchResponse(_message.Message):
    __slots__ = ("results",)
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[ConditionCheckResponse]
    def __init__(self, results: _Optional[_Iterable[_Union[ConditionCheckResponse, _Mapping]]] = ...) -> None: ...

class GetCheckResultRequest(_message.Message):
    __slots__ = ("return_id", "sku")
    RETURN_ID_FIELD_NUMBER: _ClassVar[int]
    SKU_FIELD_NUMBER: _ClassVar[int]
    return_id: str
    sku: str
    def __init__(self, return_id: _Optional[str] = ..., sku: _Optional[str] = ...) -> None: ...

class ConditionCheckResponse(_message.Message):
    __slots__ = ("return_id", "sku", "decision", "confidence_score", "reason", "requires_manual_review", "checked_at")
    RETURN_ID_FIELD_NUMBER: _ClassVar[int]
    SKU_FIELD_NUMBER: _ClassVar[int]
    DECISION_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    REQUIRES_MANUAL_REVIEW_FIELD_NUMBER: _ClassVar[int]
    CHECKED_AT_FIELD_NUMBER: _ClassVar[int]
    return_id: str
    sku: str
    decision: Decision
    confidence_score: float
    reason: str
    requires_manual_review: bool
    checked_at: str
    def __init__(self, return_id: _Optional[str] = ..., sku: _Optional[str] = ..., decision: _Optional[_Union[Decision, str]] = ..., confidence_score: _Optional[float] = ..., reason: _Optional[str] = ..., requires_manual_review: _Optional[bool] = ..., checked_at: _Optional[str] = ...) -> None: ...
