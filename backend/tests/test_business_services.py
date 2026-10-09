import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.bookings import create_booking as create_booking_route
from app.api.orders import create_order as create_order_route
from app.core.database import Base
from app.models import (
    Customer,
    Order,
    Product,
    Service,
    User,
    Workspace,
    WorkspaceMember,
)
from app.schemas.booking import BookingCreate, BookingUpdate
from app.schemas.order import OrderCreate, OrderItemCreate
from app.schemas.workspace import WorkspaceCreate
from app.services import booking_service, order_service, product_service
from app.services.ai_provider import GeminiProvider, MockAIProvider, get_ai_provider
from app.core.config import settings


class BusinessServiceTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.addCleanup(engine.dispose)
        self.db = sessionmaker(bind=engine)()
        self.addCleanup(self.db.close)

        user = User(
            name="QA Tester",
            email="qa@example.test",
            password_hash="not-used",
            status="active",
            is_verified=False,
        )
        self.db.add(user)
        self.db.commit()

        self.workspace = Workspace(
            owner_user_id=user.id,
            name="Primary",
            type="business",
            status="active",
        )
        self.other_workspace = Workspace(
            owner_user_id=user.id,
            name="Other",
            type="business",
            status="active",
        )
        self.db.add_all([self.workspace, self.other_workspace])
        self.db.commit()
        self.db.add(
            WorkspaceMember(
                workspace_id=self.workspace.id,
                user_id=user.id,
                role="owner",
                status="active",
            )
        )
        self.db.commit()
        self.user = user

        self.product = Product(
            workspace_id=self.workspace.id,
            name="Original product name",
            price=Decimal("12.50"),
            currency="BDT",
            stock_quantity=5,
            is_available=True,
            language="en",
            status="active",
        )
        self.other_product = Product(
            workspace_id=self.other_workspace.id,
            name="Other workspace product",
            price=Decimal("50.00"),
            currency="BDT",
            stock_quantity=5,
            is_available=True,
            language="en",
            status="active",
        )
        self.service = Service(
            workspace_id=self.workspace.id,
            name="Consultation",
            duration_minutes=30,
            capacity=1,
            currency="BDT",
            status="active",
        )
        self.other_service = Service(
            workspace_id=self.other_workspace.id,
            name="Other workspace service",
            duration_minutes=30,
            capacity=1,
            currency="BDT",
            status="active",
        )
        self.inactive_service = Service(
            workspace_id=self.workspace.id,
            name="Inactive service",
            duration_minutes=30,
            capacity=1,
            currency="BDT",
            status="inactive",
        )
        self.db.add_all([
            self.product,
            self.other_product,
            self.service,
            self.other_service,
            self.inactive_service,
        ])
        self.customer = Customer(
            workspace_id=self.workspace.id,
            display_name="Customer",
            consent_status="unknown",
        )
        self.other_customer = Customer(
            workspace_id=self.other_workspace.id,
            display_name="Other customer",
            consent_status="unknown",
        )
        self.db.add_all([self.customer, self.other_customer])
        self.db.commit()

    def order_data(self, product_id, *, price="0.01", name="Tampered name"):
        return OrderCreate(
            items=[
                OrderItemCreate(
                    product_id=product_id,
                    product_name_snapshot=name,
                    unit_price_snapshot=Decimal(price),
                    quantity=2,
                )
            ],
            delivery_fee=Decimal("3.00"),
        )

    def test_linked_order_uses_product_name_price_and_server_calculated_total(self):
        order = order_service.create_order(
            self.db,
            self.workspace.id,
            self.order_data(self.product.id),
        )

        self.assertEqual(order.items[0].product_name_snapshot, self.product.name)
        self.assertEqual(order.items[0].unit_price_snapshot, Decimal("12.50"))
        self.assertEqual(order.items[0].line_total, Decimal("25.00"))
        self.assertEqual(order.subtotal, Decimal("25.00"))
        self.assertEqual(order.total, Decimal("28.00"))

    def test_order_rejects_product_from_another_workspace(self):
        with self.assertRaisesRegex(ValueError, "Product not found"):
            order_service.create_order(
                self.db,
                self.workspace.id,
                self.order_data(self.other_product.id),
            )

        self.assertEqual(self.db.query(Order).count(), 0)

    def test_order_rejects_customer_from_another_workspace(self):
        data = OrderCreate(
            customer_id=self.other_customer.id,
            items=[
                OrderItemCreate(
                    product_name_snapshot="External item",
                    unit_price_snapshot=Decimal("5.00"),
                    quantity=1,
                )
            ],
        )
        with self.assertRaisesRegex(ValueError, "Customer not found"):
            order_service.create_order(self.db, self.workspace.id, data)

    def test_order_route_returns_bad_request_for_foreign_product(self):
        with self.assertRaises(HTTPException) as raised:
            create_order_route(
                self.workspace.id,
                self.order_data(self.other_product.id),
                self.user,
                self.db,
            )

        self.assertEqual(raised.exception.status_code, 400)

    def test_booking_rejects_service_from_another_workspace(self):
        starts_at = datetime.now() + timedelta(days=1)
        with self.assertRaisesRegex(ValueError, "Service not found"):
            booking_service.create_booking(
                self.db,
                self.workspace.id,
                BookingCreate(
                    service_id=self.other_service.id,
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(minutes=30),
                ),
            )

    def test_booking_route_returns_bad_request_for_foreign_service(self):
        starts_at = datetime.now() + timedelta(days=1)
        with self.assertRaises(HTTPException) as raised:
            create_booking_route(
                self.workspace.id,
                BookingCreate(
                    service_id=self.other_service.id,
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(minutes=30),
                ),
                self.user,
                self.db,
            )

        self.assertEqual(raised.exception.status_code, 400)

    def test_booking_rejects_customer_from_another_workspace(self):
        starts_at = datetime.now() + timedelta(days=1)
        with self.assertRaisesRegex(ValueError, "Customer not found"):
            booking_service.create_booking(
                self.db,
                self.workspace.id,
                BookingCreate(
                    customer_id=self.other_customer.id,
                    service_id=self.service.id,
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(minutes=30),
                ),
            )

    def test_booking_rejects_inactive_service_and_invalid_time_range(self):
        starts_at = datetime.now() + timedelta(days=1)
        with self.assertRaisesRegex(ValueError, "not available"):
            booking_service.create_booking(
                self.db,
                self.workspace.id,
                BookingCreate(
                    service_id=self.inactive_service.id,
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(minutes=30),
                ),
            )

        with self.assertRaisesRegex(ValueError, "same timezone format"):
            booking_service.create_booking(
                self.db,
                self.workspace.id,
                BookingCreate(
                    service_id=self.service.id,
                    starts_at=starts_at,
                    ends_at=(starts_at + timedelta(minutes=30)).astimezone(),
                ),
            )

        with self.assertRaisesRegex(ValueError, "after its start"):
            booking_service.create_booking(
                self.db,
                self.workspace.id,
                BookingCreate(
                    service_id=self.service.id,
                    starts_at=starts_at,
                    ends_at=starts_at,
                ),
            )

    def test_booking_respects_capacity_and_allows_adjacent_slots(self):
        starts_at = datetime.now() + timedelta(days=1)
        first = BookingCreate(
            service_id=self.service.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=30),
        )
        booking_service.create_booking(self.db, self.workspace.id, first)

        with self.assertRaisesRegex(ValueError, "not available"):
            booking_service.create_booking(self.db, self.workspace.id, first)

        adjacent = BookingCreate(
            service_id=self.service.id,
            starts_at=starts_at + timedelta(minutes=30),
            ends_at=starts_at + timedelta(minutes=60),
        )
        booking_service.create_booking(self.db, self.workspace.id, adjacent)

    def test_booking_capacity_allows_multiple_overlapping_requests(self):
        self.service.capacity = 2
        self.db.commit()
        starts_at = datetime.now() + timedelta(days=1)
        booking_data = BookingCreate(
            service_id=self.service.id,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=30),
        )

        booking_service.create_booking(self.db, self.workspace.id, booking_data)
        booking_service.create_booking(self.db, self.workspace.id, booking_data)
        with self.assertRaisesRegex(ValueError, "not available"):
            booking_service.create_booking(self.db, self.workspace.id, booking_data)

    def test_rescheduling_booking_checks_time_range_and_capacity(self):
        starts_at = datetime.now() + timedelta(days=1)
        booking = booking_service.create_booking(
            self.db,
            self.workspace.id,
            BookingCreate(
                service_id=self.service.id,
                starts_at=starts_at,
                ends_at=starts_at + timedelta(minutes=30),
            ),
        )
        other_booking = booking_service.create_booking(
            self.db,
            self.workspace.id,
            BookingCreate(
                service_id=self.service.id,
                starts_at=starts_at + timedelta(minutes=30),
                ends_at=starts_at + timedelta(minutes=60),
            ),
        )

        with self.assertRaisesRegex(ValueError, "not available"):
            booking_service.update_booking(
                self.db,
                booking,
                BookingUpdate(
                    starts_at=other_booking.starts_at,
                    ends_at=other_booking.ends_at,
                ),
            )

        with self.assertRaisesRegex(ValueError, "after its start"):
            booking_service.update_booking(
                self.db,
                booking,
                BookingUpdate(starts_at=starts_at, ends_at=starts_at),
            )

    def test_restoring_stock_makes_active_product_available(self):
        self.product.stock_quantity = 0
        self.product.is_available = False
        self.db.commit()

        product_service.adjust_stock(self.db, self.product, 3)

        self.assertEqual(self.product.stock_quantity, 3)
        self.assertTrue(self.product.is_available)

    def test_workspace_names_are_trimmed_and_whitespace_only_is_rejected(self):
        self.assertEqual(WorkspaceCreate(name="  Shop  ").name, "Shop")
        with self.assertRaises(ValueError):
            WorkspaceCreate(name="   ")


class AIProviderConfigurationTests(unittest.TestCase):
    def test_mock_is_selected_only_when_explicitly_configured(self):
        with patch.object(settings, "AI_PROVIDER", "mock"):
            self.assertIsInstance(get_ai_provider(), MockAIProvider)

    def test_real_provider_without_key_fails_instead_of_using_mock(self):
        with (
            patch.object(settings, "AI_PROVIDER", "openai"),
            patch.object(settings, "OPENAI_API_KEY", None),
        ):
            with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY is required"):
                get_ai_provider()

    def test_gemini_without_key_fails_instead_of_using_mock(self):
        with (
            patch.object(settings, "AI_PROVIDER", "gemini"),
            patch.object(settings, "GEMINI_API_KEY", None),
        ):
            with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY is required"):
                get_ai_provider()

    def test_gemini_provider_uses_the_configured_model(self):
        with (
            patch.object(settings, "AI_PROVIDER", "gemini"),
            patch.object(settings, "GEMINI_API_KEY", "test-key"),
            patch.object(settings, "GEMINI_MODEL", "gemini-test"),
            patch("app.services.ai_provider.importlib.import_module"),
        ):
            provider = get_ai_provider()

        self.assertIsInstance(provider, GeminiProvider)
        self.assertEqual(provider.model, "gemini-test")

    def test_unknown_provider_is_rejected(self):
        with patch.object(settings, "AI_PROVIDER", "unknown"):
            with self.assertRaisesRegex(ValueError, "Unsupported AI_PROVIDER"):
                get_ai_provider()


class GeminiProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_generate_response_sends_history_and_closes_async_client(self):
        request = {}

        class FakeModels:
            async def generate_content(self, **kwargs):
                request.update(kwargs)
                return type("Response", (), {"text": "  Gemini reply  "})()

        class FakeAsyncClient:
            models = FakeModels()
            closed = False

            async def aclose(self):
                self.closed = True

        async_client = FakeAsyncClient()
        client = type("Client", (), {"aio": async_client})()
        sdk_client_factory = Mock(return_value=client)
        sdk = type(
            "GeminiSDK",
            (),
            {"Client": staticmethod(sdk_client_factory)},
        )()

        with patch(
            "app.services.ai_provider.importlib.import_module",
            return_value=sdk,
        ) as import_module:
            provider = GeminiProvider("test-key", "gemini-test")
            result = await provider.generate_response(
                [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi"},
                ],
                system_prompt="Be concise",
                max_tokens=123,
            )

        import_module.assert_called_once_with("google.genai")
        sdk_client_factory.assert_called_once_with(api_key="test-key")
        self.assertEqual(result, "Gemini reply")
        self.assertEqual(request["model"], "gemini-test")
        self.assertEqual(
            request["contents"],
            [
                {"role": "user", "parts": [{"text": "Hello"}]},
                {"role": "model", "parts": [{"text": "Hi"}]},
            ],
        )
        self.assertEqual(
            request["config"],
            {"max_output_tokens": 123, "system_instruction": "Be concise"},
        )
        self.assertTrue(async_client.closed)


if __name__ == "__main__":
    unittest.main()
