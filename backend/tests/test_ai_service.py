import unittest
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import (
    BusinessProfile,
    Conversation,
    FAQ,
    Product,
    Service,
    User,
    Workspace,
)
from app.services.ai_provider import MockAIProvider
from app.services.ai_service import generate_ai_response


class AIServiceContextTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        self.addCleanup(engine.dispose)
        self.db = sessionmaker(bind=engine)()
        self.addCleanup(self.db.close)

        user = User(
            name="AI Test User",
            email="ai-test@example.test",
            password_hash="not-used",
            status="active",
            is_verified=False,
        )
        self.db.add(user)
        self.db.commit()

        self.business_workspace = Workspace(
            owner_user_id=user.id,
            name="Test Business",
            type="business",
            status="active",
        )
        self.other_workspace = Workspace(
            owner_user_id=user.id,
            name="Other Business",
            type="business",
            status="active",
        )
        self.personal_workspace = Workspace(
            owner_user_id=user.id,
            name="Personal",
            type="personal",
            status="active",
        )
        self.db.add_all(
            [
                self.business_workspace,
                self.other_workspace,
                self.personal_workspace,
            ]
        )
        self.db.commit()

    async def _generate(self, workspace):
        conversation = Conversation(
            workspace_id=workspace.id,
            owner_user_id=workspace.owner_user_id,
            channel="web",
            status="active",
        )
        self.db.add(conversation)
        self.db.commit()

        provider = type("Provider", (), {})()
        provider.generate_response = AsyncMock(return_value="Grounded answer")
        with patch("app.services.ai_service.get_ai_provider", return_value=provider):
            result = await generate_ai_response(
                self.db, conversation, "দাম কত?"
            )

        self.assertEqual(result, "Grounded answer")
        return provider.generate_response.await_args.kwargs["system_prompt"]

    async def test_business_prompt_uses_only_published_workspace_knowledge(self):
        self.db.add(
            BusinessProfile(
                workspace_id=self.business_workspace.id,
                business_name="Sample Shop",
                opening_hours="10:00-18:00",
            )
        )
        self.db.add_all(
            [
                FAQ(
                    workspace_id=self.business_workspace.id,
                    question="What is the return policy?",
                    answer="Returns within 7 days.",
                    question_bn="ফেরত নীতি কী?",
                    answer_bn="৭ দিনের মধ্যে ফেরত।",
                    question_en="What is the return policy?",
                    answer_en="Returns within 7 days.",
                    status="published",
                ),
                FAQ(
                    workspace_id=self.business_workspace.id,
                    question="Draft-only secret",
                    answer="Must not be shared.",
                    status="draft",
                ),
                FAQ(
                    workspace_id=self.other_workspace.id,
                    question="Other workspace FAQ",
                    answer="Must not leak.",
                    status="published",
                ),
                Product(
                    workspace_id=self.business_workspace.id,
                    name="Tea",
                    description="Black tea",
                    price=Decimal("120.00"),
                    currency="BDT",
                    stock_quantity=3,
                    is_available=True,
                    status="active",
                ),
                Product(
                    workspace_id=self.business_workspace.id,
                    name="Archived item",
                    price=Decimal("1.00"),
                    currency="BDT",
                    stock_quantity=1,
                    is_available=True,
                    status="archived",
                ),
                Product(
                    workspace_id=self.other_workspace.id,
                    name="Other shop item",
                    price=Decimal("2.00"),
                    currency="BDT",
                    stock_quantity=1,
                    is_available=True,
                    status="active",
                ),
                Service(
                    workspace_id=self.business_workspace.id,
                    name="Consultation",
                    description="One-on-one session",
                    duration_minutes=30,
                    price=Decimal("500.00"),
                    currency="BDT",
                    status="active",
                ),
            ]
        )
        self.db.commit()

        prompt = await self._generate(self.business_workspace)

        self.assertIn("Product name, description, price, or stock", prompt)
        self.assertIn("Sample Shop", prompt)
        self.assertIn("10:00-18:00", prompt)
        self.assertIn("৭ দিনের মধ্যে ফেরত।", prompt)
        self.assertIn("Tea", prompt)
        self.assertIn("120.00 BDT", prompt)
        self.assertIn("recorded stock 3", prompt)
        self.assertIn("Consultation", prompt)
        self.assertIn("500.00 BDT", prompt)
        self.assertIn("cannot create orders/bookings", prompt)
        self.assertNotIn("Draft-only secret", prompt)
        self.assertNotIn("Must not be shared.", prompt)
        self.assertNotIn("Other workspace FAQ", prompt)
        self.assertNotIn("Other shop item", prompt)
        self.assertNotIn("Archived item", prompt)

    async def test_personal_prompt_does_not_include_business_data(self):
        self.db.add(
            Product(
                workspace_id=self.business_workspace.id,
                name="Private business catalog item",
                price=Decimal("5.00"),
                currency="BDT",
                stock_quantity=1,
                is_available=True,
                status="active",
            )
        )
        self.db.commit()

        prompt = await self._generate(self.personal_workspace)

        self.assertIn("personal productivity assistant", prompt)
        self.assertIn("tasks, notes, or appointments", prompt)
        self.assertNotIn("Private business catalog item", prompt)
        self.assertNotIn("business_reference_data", prompt)


class MockAIProviderBehaviorTests(unittest.IsolatedAsyncioTestCase):
    async def test_mock_provider_does_not_invent_business_hours(self):
        response = await MockAIProvider().generate_response(
            [{"role": "user", "content": "দোকান কখন খোলা?"}]
        )

        self.assertIn("AI_PROVIDER=mock", response)
        self.assertNotIn("সকাল ৯টা", response)
        self.assertNotIn("রাত ৯টা", response)


if __name__ == "__main__":
    unittest.main()
