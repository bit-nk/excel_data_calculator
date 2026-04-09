import enum


class Platform(str, enum.Enum):
    AWS = "aws"
    MONGODB = "mongodb"
    DATADOG = "datadog"
    CONFLUENT = "confluent"
    SINGLESTORE = "singlestore"
    HARNESS = "harness"


class CostCategory(str, enum.Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    MONITORING = "monitoring"
    STREAMING = "streaming"
    PLATFORM = "platform"
    LICENSE = "license"
    SUPPORT = "support"
    OTHER = "other"


class CostAllocationType(str, enum.Enum):
    DIRECT = "direct"
    SHARED = "shared"
    PLATFORM_ENGINEERING = "platform_engineering"
    UNALLOCATED = "unallocated"


class ReportStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    APPROVED = "approved"
    PUBLISHED = "published"
    FAILED = "failed"


class ChargebackStatus(str, enum.Enum):
    PENDING = "pending"
    CALCULATED = "calculated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    SENT_TO_ACCOUNTING = "sent_to_accounting"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    FINANCE = "finance"
    PORTFOLIO_MANAGER = "portfolio_manager"
    VIEWER = "viewer"


class SharedCostMethod(str, enum.Enum):
    PRO_RATA = "pro_rata"
    EQUAL_SPLIT = "equal_split"
    USAGE_BASED = "usage_based"
    FIXED_PERCENTAGE = "fixed_percentage"
