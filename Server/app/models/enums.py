from enum import Enum


class KnowledgeItemType(Enum):
    FILE = "FILE"
    MANUALLY = "MANUALLY"

class FileStatus(Enum):
    UPLOADED = "UPLOADED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    EMBEDDING = "EMBEDDING"

class ReviewStatus(Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"

class ReviewType(Enum):
    NEGLECT = "NEGLECT"
    REPLACE = "REPLACE"
    FUSION = "FUSION"