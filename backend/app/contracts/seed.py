from datetime import datetime

from pydantic import Field

from app.contracts.common import ContractModel


class SeedDomainBatch(ContractModel):
    domain: str
    schema_version: str
    record_count: int = Field(ge=0)
    file: str
    checksum_sha256: str
    load_order: int = Field(ge=1)


class SeedProvenance(ContractModel):
    source: str
    generator: str | None = None
    notes: str | None = None


class SeedManifest(ContractModel):
    manifest_version: str
    dataset_id: str
    dataset_version: str
    environment: str
    synthetic: bool = True
    created_by: str
    created_at: datetime
    idempotency_key: str
    manifest_checksum_sha256: str
    rollback_from_dataset_version: str | None = None
    provenance: SeedProvenance
    domains: list[SeedDomainBatch] = Field(min_length=1)
