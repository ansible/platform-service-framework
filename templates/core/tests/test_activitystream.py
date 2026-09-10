"""Tests for DAB activity-stream integration."""

import pytest

from apps.core.models import Organization


@pytest.mark.django_db
def test_auditable_models_create_activity_stream_entries():
    organization = Organization.objects.create(name="Audited organization")

    entries = organization.activity_stream_entries

    assert entries.count() == 1
    assert entries.first().operation == "create"
