from app.schemas.user import (
    UserBase, UserCreate, UserLogin, UserResponse, Token, TokenData,
)
from app.schemas.workspace import (
    WorkspaceBase, WorkspaceCreate, WorkspaceResponse,
    WorkspaceMemberBase, WorkspaceMemberCreate, WorkspaceMemberResponse,
)
from app.schemas.task import (
    TaskBase, TaskCreate, TaskUpdate, TaskResponse,
)
from app.schemas.note import (
    NoteBase, NoteCreate, NoteUpdate, NoteResponse,
)
from app.schemas.appointment import (
    AppointmentBase, AppointmentCreate, AppointmentUpdate, AppointmentResponse,
)
from app.schemas.business_profile import (
    BusinessProfileBase, BusinessProfileCreate, BusinessProfileUpdate, BusinessProfileResponse,
)
from app.schemas.faq import (
    FAQBase, FAQCreate, FAQUpdate, FAQResponse,
)
from app.schemas.product import (
    ProductBase, ProductCreate, ProductUpdate, ProductResponse, InventoryAdjustment,
)
from app.schemas.customer import (
    CustomerBase, CustomerCreate, CustomerUpdate, CustomerResponse,
)
from app.schemas.order import (
    OrderBase, OrderCreate, OrderUpdate, OrderStatusUpdate, OrderResponse,
    OrderItemBase, OrderItemCreate, OrderItemResponse,
)
from app.schemas.service import (
    ServiceBase, ServiceCreate, ServiceUpdate, ServiceResponse,
)
from app.schemas.booking import (
    BookingBase, BookingCreate, BookingUpdate, BookingStatusUpdate, BookingResponse,
)
from app.schemas.conversation import (
    ConversationBase, ConversationCreate, ConversationUpdate,
    ConversationResponse, HandoffRequest,
)
from app.schemas.message import (
    MessageBase, MessageCreate, MessageResponse,
    ChatRequest, ChatResponse,
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    # Workspace
    "WorkspaceBase", "WorkspaceCreate", "WorkspaceResponse",
    "WorkspaceMemberBase", "WorkspaceMemberCreate", "WorkspaceMemberResponse",
    # Task
    "TaskBase", "TaskCreate", "TaskUpdate", "TaskResponse",
    # Note
    "NoteBase", "NoteCreate", "NoteUpdate", "NoteResponse",
    # Appointment
    "AppointmentBase", "AppointmentCreate", "AppointmentUpdate", "AppointmentResponse",
    # Business Profile
    "BusinessProfileBase", "BusinessProfileCreate", "BusinessProfileUpdate", "BusinessProfileResponse",
    # FAQ
    "FAQBase", "FAQCreate", "FAQUpdate", "FAQResponse",
    # Product
    "ProductBase", "ProductCreate", "ProductUpdate", "ProductResponse", "InventoryAdjustment",
    # Customer
    "CustomerBase", "CustomerCreate", "CustomerUpdate", "CustomerResponse",
    # Order
    "OrderBase", "OrderCreate", "OrderUpdate", "OrderStatusUpdate", "OrderResponse",
    "OrderItemBase", "OrderItemCreate", "OrderItemResponse",
    # Service
    "ServiceBase", "ServiceCreate", "ServiceUpdate", "ServiceResponse",
    # Booking
    "BookingBase", "BookingCreate", "BookingUpdate", "BookingStatusUpdate", "BookingResponse",
    # Conversation
    "ConversationBase", "ConversationCreate", "ConversationUpdate",
    "ConversationResponse", "HandoffRequest",
    # Message
    "MessageBase", "MessageCreate", "MessageResponse",
    "ChatRequest", "ChatResponse",
]