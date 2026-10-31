# client.py – gRPC client for the Article Condition Service
# Stands in for the WMS scanner app that sends the recorded condition of a returned article.

import os
from datetime import datetime, timezone

import grpc

from grpc_service.generated import article_condition_service_pb2 as pb2
from grpc_service.generated import article_condition_service_pb2_grpc as pb2_grpc

SERVER_ADDRESS = os.environ.get("GRPC_SERVER_ADDRESS", "localhost:50051")
DEADLINE_SECONDS = 2   # max. time we wait for an answer


class ConditionServiceClient:
    """Wraps the generated stub so callers only deal with simple Python values."""

    def __init__(self, address: str = SERVER_ADDRESS):
        self.channel = grpc.insecure_channel(address)
        self.stub = pb2_grpc.ArticleConditionServiceStub(self.channel)

    def check(self, return_id: str, sku: str, condition: int, *, tags: bool = True,
              packaging: bool = True, images: list[str] | None = None,
              note: str = "") -> pb2.ConditionCheckResponse:
        request = build_request(return_id, sku, condition, tags, packaging, images, note)
        return self.stub.CheckCondition(request, timeout=DEADLINE_SECONDS)

    def check_batch(self, requests: list[pb2.ConditionCheckRequest]) -> list[pb2.ConditionCheckResponse]:
        response = self.stub.CheckConditionBatch(
            pb2.ConditionCheckBatchRequest(items=requests), timeout=DEADLINE_SECONDS)
        return list(response.results)

    def get_result(self, return_id: str, sku: str) -> pb2.ConditionCheckResponse:
        return self.stub.GetCheckResult(
            pb2.GetCheckResultRequest(return_id=return_id, sku=sku), timeout=DEADLINE_SECONDS)


def build_request(return_id, sku, condition, tags=True, packaging=True, images=None, note=""):
    """Create the request message as the WMS scanner would send it."""
    return pb2.ConditionCheckRequest(
        return_id=return_id,
        sku=sku,
        observed_condition=condition,
        image_urls=images or [],
        tags_present=tags,
        original_packaging=packaging,
        inspector_note=note,
        inspected_at=datetime.now(timezone.utc).isoformat(),
    )


def show(result: pb2.ConditionCheckResponse) -> None:
    """Print one result in a readable way."""
    print(f"   {result.return_id}/{result.sku}: {pb2.Decision.Name(result.decision)} "
          f"(confidence {result.confidence_score:.2f}) - {result.reason}")


def show_error(error: grpc.RpcError) -> None:
    print(f"   gRPC error {error.code().name}: {error.details()}")


def main() -> None:
    client = ConditionServiceClient()
    photo = ["https://wms.example.com/photos/1.jpg"]

    print("1) Single checks - one scenario per decision path")
    scenarios = [
        ("RET-2026-00457", "SH-BLZ-042-M", pb2.AS_NEW, True, True, photo, "As new, everything complete"),
        ("RET-2026-00458", "SH-SWT-008-L", pb2.DAMAGED, True, True, photo, "Damaged on arrival?"),
        ("RET-2026-00460", "SH-SNK-115-42", pb2.AS_NEW, False, False, photo, "As new, tags removed"),
        ("RET-2026-00461", "SH-JNS-033-32", pb2.VISIBLY_WORN, False, False, photo, "Clearly worn"),
        ("RET-2026-00462", "SH-JKT-007-M", pb2.MISSING_PARTS, True, False, [], "Missing parts, no photos"),
    ]
    for return_id, sku, condition, tags, packaging, images, label in scenarios:
        print(f"  - {label}")
        show(client.check(return_id, sku, condition, tags=tags, packaging=packaging, images=images))

    print("\n2) Batch check - a parcel with two articles")
    results = client.check_batch([
        build_request("RET-2026-00459", "SH-DRS-021-S", pb2.MINOR_WEAR, images=photo),
        build_request("RET-2026-00459", "SH-SHR-017-M", pb2.AS_NEW, images=photo),
    ])
    for result in results:
        show(result)

    print("\n3) Retrieve a stored result (audit)")
    show(client.get_result("RET-2026-00457", "SH-BLZ-042-M"))

    print("\n4) Error scenarios")
    error_cases = [
        ("Missing condition -> INVALID_ARGUMENT",
         lambda: client.check("RET-2026-00457", "SH-BLZ-042-M", pb2.OBSERVED_CONDITION_UNSPECIFIED)),
        ("Missing return_id -> INVALID_ARGUMENT",
         lambda: client.check("", "SH-BLZ-042-M", pb2.AS_NEW)),
        ("Unknown result -> NOT_FOUND",
         lambda: client.get_result("RET-9999", "XYZ")),
        ("Slow server -> DEADLINE_EXCEEDED",
         lambda: client.check("RET-2026-00457", "SH-BLZ-042-M", pb2.AS_NEW, note="SIMULATE_SLOW")),
    ]
    for label, call in error_cases:
        print(f"  - {label}")
        try:
            call()
        except grpc.RpcError as error:
            show_error(error)


if __name__ == "__main__":
    try:
        main()
    except grpc.RpcError as error:
        if error.code() == grpc.StatusCode.UNAVAILABLE:
            print("Cannot reach the gRPC service. Is it running? (python -m grpc_service.server)")
        else:
            raise