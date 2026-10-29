# server.py – gRPC Article Condition Service
# Evaluates the condition of a returned article (recorded in the WMS) and recommends
# ACCEPT, REJECT or MANUAL_REVIEW.

import logging
import time
from concurrent import futures
from datetime import datetime, timezone

import grpc

from grpc_service.generated import article_condition_service_pb2 as pb2
from grpc_service.generated import article_condition_service_pb2_grpc as pb2_grpc

PORT = 50051
MIN_CONFIDENCE = 0.60      # below this, ACCEPT/REJECT is not trusted -> MANUAL_REVIEW
NO_IMAGES_PENALTY = 0.10   # missing photos make the decision less certain

# --- Decision rules -------------------------------------------------------------
# Rules for every condition except AS_NEW (AS_NEW depends on tags/packaging, see evaluate()).
# condition -> (decision, confidence, reason)
RULES = {
    pb2.MINOR_WEAR: (pb2.MANUAL_REVIEW, 0.55, "Minor signs of wear - resale value must be assessed"),
    pb2.MISSING_TAGS: (pb2.MANUAL_REVIEW, 0.50, "Tags or hologram missing - possible wardrobing"),
    pb2.DAMAGED: (pb2.MANUAL_REVIEW, 0.40, "Damaged - check if defect existed at delivery (warranty claim)"),
    pb2.VISIBLY_WORN: (pb2.REJECT, 0.85, "Visibly worn - not resellable"),
    pb2.MISSING_PARTS: (pb2.REJECT, 0.80, "Accessories or parts missing"),
}


def evaluate(request: pb2.ConditionCheckRequest) -> tuple[int, float, str]:
    """Apply the business rules to one article. Returns (decision, confidence, reason)."""
    if request.observed_condition == pb2.AS_NEW:
        if request.tags_present and request.original_packaging:
            decision, confidence, reason = pb2.ACCEPT, 0.95, "As new, tags and original packaging present"
        elif request.tags_present:
            decision, confidence, reason = pb2.ACCEPT, 0.85, "As new with tags, original packaging missing"
        else:
            decision, confidence, reason = pb2.MANUAL_REVIEW, 0.60, "As new but tags removed - possible wardrobing"
    else:
        decision, confidence, reason = RULES[request.observed_condition]

    # General rule 1: no photos -> less certain
    if not request.image_urls:
        confidence = round(confidence - NO_IMAGES_PENALTY, 2)
        reason += "; no photos (confidence reduced)"

    # General rule 2: weak automatic decisions are handed to a human
    if decision in (pb2.ACCEPT, pb2.REJECT) and confidence < MIN_CONFIDENCE:
        decision = pb2.MANUAL_REVIEW
        reason += "; confidence below threshold -> manual review"

    return decision, confidence, reason


def validate(request: pb2.ConditionCheckRequest, context: grpc.ServicerContext) -> None:
    """Reject incomplete requests with INVALID_ARGUMENT (ends the call immediately)."""
    if not request.return_id or not request.sku:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, "return_id and sku are required")
    if request.observed_condition == pb2.OBSERVED_CONDITION_UNSPECIFIED:
        context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                      f"observed_condition missing for {request.return_id}/{request.sku}")


# --- The service ----------------------------------------------------------------
class ArticleConditionService(pb2_grpc.ArticleConditionServiceServicer):
    """Implements the three RPCs defined in article_condition_service.proto."""

    def __init__(self):
        # Stored results for GetCheckResult: (return_id, sku) -> response
        self.results: dict[tuple[str, str], pb2.ConditionCheckResponse] = {}

    def _check(self, request: pb2.ConditionCheckRequest) -> pb2.ConditionCheckResponse:
        """Evaluate one (already validated) article and store the result."""
        if request.inspector_note == "SIMULATE_SLOW":   # demo hook for the client deadline
            time.sleep(3)

        decision, confidence, reason = evaluate(request)
        response = pb2.ConditionCheckResponse(
            return_id=request.return_id,
            sku=request.sku,
            decision=decision,
            confidence_score=confidence,
            reason=reason,
            requires_manual_review=(decision == pb2.MANUAL_REVIEW),
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
        self.results[(request.return_id, request.sku)] = response
        logging.info("%s/%s -> %s (%.2f)", request.return_id, request.sku,
                     pb2.Decision.Name(decision), confidence)
        return response

    def CheckCondition(self, request, context):
        validate(request, context)
        return self._check(request)

    def CheckConditionBatch(self, request, context):
        if not request.items:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "batch contains no items")
        for item in request.items:          # validate ALL items first (all-or-nothing)
            validate(item, context)
        return pb2.ConditionCheckBatchResponse(results=[self._check(item) for item in request.items])

    def GetCheckResult(self, request, context):
        result = self.results.get((request.return_id, request.sku))
        if result is None:
            context.abort(grpc.StatusCode.NOT_FOUND,
                          f"No check result for {request.return_id}/{request.sku}")
        return result


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ArticleConditionServiceServicer_to_server(ArticleConditionService(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    logging.info("Article Condition Service listening on port %d", PORT)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    serve()