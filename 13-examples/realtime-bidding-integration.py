"""
Real-Time Bidding Integration Example

Demonstrates how to integrate Veylan VisionOS with RTB ad exchanges.
Shows end-to-end flow from bid request to response with Titan Memory
and Trading Agent.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, Dict
import json


@dataclass
class BidRequest:
    """OpenRTB-compatible bid request"""
    id: str
    imp: list  # Impressions
    site: Optional[dict] = None
    app: Optional[dict] = None
    device: dict = None
    user: dict = None
    at: int = 2  # Auction type: 2 = second price
    tmax: int = 120  # Timeout in ms
    cur: list = None  # Currencies


@dataclass
class BidResponse:
    """OpenRTB-compatible bid response"""
    id: str  # Must match request ID
    seatbid: list  # Seat bids
    bidid: str
    cur: str = "USD"


class RTBIntegration:
    """
    Integration layer between SSP and Veylan VisionOS
    """

    def __init__(self, titan_memory, trading_agent):
        self.titan_memory = titan_memory
        self.trading_agent = trading_agent
        self.latency_budget_ms = 50  # RTB latency SLA

    async def handle_bid_request(self, bid_request: BidRequest) -> Optional[BidResponse]:
        """
        Handle incoming bid request from SSP

        Must complete within 50ms to meet RTB latency SLA
        """
        start_time = time.time()

        try:
            # Step 1: Quick validation (< 1ms)
            if not self._validate_request(bid_request):
                return None

            # Step 2: Match to active campaigns (< 5ms)
            # Query Titan Memory for campaigns targeting this inventory
            matching_campaigns = await self._find_matching_campaigns(bid_request)

            if not matching_campaigns:
                return None

            # Step 3: Predict value and make bid decision (< 20ms)
            bid_decisions = []
            for campaign in matching_campaigns:
                decision = await self.trading_agent.make_bid_decision(
                    bid_request=bid_request,
                    campaign=campaign,
                    time_budget_ms=self._remaining_time_ms(start_time)
                )

                if decision and decision["bid"]:
                    bid_decisions.append(decision)

            if not bid_decisions:
                return None

            # Step 4: Select best bid (< 2ms)
            best_bid = max(bid_decisions, key=lambda x: x["bid_price"])

            # Step 5: Construct response (< 2ms)
            response = self._construct_bid_response(bid_request, best_bid)

            # Step 6: Log for analytics (async, doesn't block)
            asyncio.create_task(self._log_bid_event(bid_request, response))

            elapsed_ms = (time.time() - start_time) * 1000
            if elapsed_ms > self.latency_budget_ms:
                print(f"⚠️  Bid response took {elapsed_ms:.1f}ms (SLA: {self.latency_budget_ms}ms)")

            return response

        except Exception as e:
            print(f"❌ Error processing bid request: {e}")
            return None

    def _validate_request(self, bid_request: BidRequest) -> bool:
        """Quick validation of bid request"""
        # Must have at least one impression
        if not bid_request.imp:
            return False

        # Must have device or user info
        if not bid_request.device and not bid_request.user:
            return False

        # Check timeout
        if bid_request.tmax < 50:  # Less than our minimum
            return False

        return True

    async def _find_matching_campaigns(self, bid_request: BidRequest) -> list:
        """
        Find campaigns that match this bid request

        Uses Titan Memory to query active campaigns with matching targeting
        """
        # Extract targeting signals from bid request
        targeting_signals = self._extract_targeting_signals(bid_request)

        # Query Titan Memory for matching campaigns
        # In production, this would be optimized with pre-computed indexes
        matching_campaigns = []

        # Simulated query (in production, would use actual Titan Memory)
        # titan_memory.query("campaign", filters={"status": "active", ...})

        # For demo, return mock campaigns
        mock_campaigns = [
            {
                "campaign_id": "campaign_001",
                "advertiser": "TechCo",
                "budget_remaining": 5000,
                "target_cpa": 25.00,
                "target_audiences": ["tech_millennials"],
                "max_bid": 2.50
            }
        ]

        return mock_campaigns

    def _extract_targeting_signals(self, bid_request: BidRequest) -> dict:
        """Extract targeting signals from bid request"""
        signals = {}

        # Device signals
        if bid_request.device:
            signals["device_type"] = bid_request.device.get("devicetype")
            signals["os"] = bid_request.device.get("os")
            signals["geo"] = bid_request.device.get("geo", {})

        # User signals
        if bid_request.user:
            signals["user_id"] = bid_request.user.get("id")
            signals["demographics"] = {
                "age": bid_request.user.get("yob"),
                "gender": bid_request.user.get("gender")
            }

        # Impression signals
        if bid_request.imp:
            imp = bid_request.imp[0]  # First impression
            signals["ad_format"] = "banner" if imp.get("banner") else "video"
            signals["floor_price"] = imp.get("bidfloor", 0.0)

        return signals

    def _construct_bid_response(self, bid_request: BidRequest, bid_decision: dict) -> BidResponse:
        """Construct OpenRTB bid response"""
        return BidResponse(
            id=bid_request.id,
            bidid=f"bid_{bid_request.id}_{int(time.time())}",
            seatbid=[
                {
                    "bid": [
                        {
                            "id": "1",
                            "impid": bid_request.imp[0]["id"],
                            "price": bid_decision["bid_price"],
                            "adid": bid_decision["creative_id"],
                            "adm": self._get_creative_markup(bid_decision["creative_id"]),
                            "adomain": ["techco.com"],
                            "cid": bid_decision["campaign_id"],
                            "crid": bid_decision["creative_id"],
                            "attr": []
                        }
                    ],
                    "seat": "veylan"
                }
            ],
            cur="USD"
        )

    def _get_creative_markup(self, creative_id: str) -> str:
        """Get creative ad markup (HTML/VAST)"""
        # In production, would query Titan Memory
        return f'<div class="ad" data-creative="{creative_id}">Ad Content</div>'

    async def _log_bid_event(self, bid_request: BidRequest, bid_response: Optional[BidResponse]):
        """Log bid event for analytics (async)"""
        event = {
            "timestamp": time.time(),
            "request_id": bid_request.id,
            "bid_submitted": bid_response is not None,
            "bid_price": bid_response.seatbid[0]["bid"][0]["price"] if bid_response else None
        }

        # In production, would send to Kafka/Kinesis
        print(f"📊 Logged bid event: {json.dumps(event)}")

    def _remaining_time_ms(self, start_time: float) -> float:
        """Calculate remaining time budget"""
        elapsed_ms = (time.time() - start_time) * 1000
        return max(0, self.latency_budget_ms - elapsed_ms)


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Demonstrate RTB integration"""
    print("=" * 70)
    print("Real-Time Bidding Integration Example")
    print("=" * 70)

    # Initialize (mock) components
    titan_memory = None  # Would be actual TitanMemory instance
    trading_agent = None  # Would be actual TradingAgent instance

    rtb = RTBIntegration(titan_memory, trading_agent)

    # Simulate incoming bid request
    bid_request = BidRequest(
        id="req_123456",
        imp=[
            {
                "id": "1",
                "banner": {
                    "w": 728,
                    "h": 90,
                    "pos": 1
                },
                "bidfloor": 0.50,
                "bidfloorcur": "USD"
            }
        ],
        device={
            "ua": "Mozilla/5.0...",
            "geo": {
                "country": "USA",
                "region": "CA",
                "city": "San Francisco"
            },
            "devicetype": 1,  # Mobile
            "os": "iOS"
        },
        user={
            "id": "user_abc123"
        },
        tmax=120
    )

    print(f"\n📥 Received bid request: {bid_request.id}")
    print(f"   Format: 728x90 banner")
    print(f"   Floor: $0.50")
    print(f"   Location: San Francisco, CA")

    # Process bid request
    start = time.time()
    response = await rtb.handle_bid_request(bid_request)
    elapsed_ms = (time.time() - start) * 1000

    if response:
        bid_price = response.seatbid[0]["bid"][0]["price"]
        print(f"\n✅ Bid submitted: ${bid_price:.2f}")
        print(f"   Creative ID: {response.seatbid[0]['bid'][0]['crid']}")
        print(f"   Response time: {elapsed_ms:.1f}ms")

        if elapsed_ms < 50:
            print(f"   ✓ Within SLA (< 50ms)")
        else:
            print(f"   ⚠️  Exceeded SLA")
    else:
        print(f"\n❌ No bid submitted")
        print(f"   Response time: {elapsed_ms:.1f}ms")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
