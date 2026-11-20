"""Signatures collected on Receiving, Delivery, Issue and Client Return records.

Deliberately separate from services.py: nothing here touches ProductUnit or
StockMovement. A signature is append-only evidence attached to a record.
"""

import base64
import binascii
from collections import namedtuple
from io import BytesIO

from django.core.exceptions import ValidationError
from django.db import transaction
from PIL import Image, UnidentifiedImageError

from . import constants as stock_constants
from .models import (
    ClientReturnRecord,
    DeliveryRecord,
    IssueRecord,
    ReceivingRecord,
    RecordSignature,
)
from .services import log_record_changes

MAX_IMAGE_BYTES = 204800
MAX_WIDTH = 1600
MAX_HEIGHT = 800
MAX_SIGNER_NAME = 150
MAX_ROLE_LABEL = 50

SignableRecord = namedtuple("SignableRecord", "model number_attr view_perm label")

SIGNABLE_RECORDS = {
    "receiving": SignableRecord(
        ReceivingRecord, "receiving_number", stock_constants.VIEW_RECEIVING_RECORD, "Receiving"
    ),
    "delivery": SignableRecord(
        DeliveryRecord, "delivery_number", stock_constants.VIEW_DELIVERY_RECORD, "Delivery"
    ),
    "issue": SignableRecord(
        IssueRecord, "issue_number", stock_constants.VIEW_ISSUE_RECORD, "Assignment"
    ),
    "client_return": SignableRecord(
        ClientReturnRecord, "return_number", stock_constants.VIEW_CLIENT_RETURN_RECORD, "Client Return"
    ),
}


def validate_signature_png(data):
    """Decode a data URL or bare base64 PNG and return the validated bytes."""
    if not isinstance(data, str) or not data.strip():
        raise ValidationError("A signature image is required.")
    text = data.strip()
    if text.startswith("data:"):
        header, _, text = text.partition(",")
        if not header.lower().startswith("data:image/png") or "base64" not in header.lower():
            raise ValidationError("The signature must be a PNG image.")
    text = "".join(text.split())
    try:
        raw = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError):
        raise ValidationError("The signature image is not valid base64.")
    if not raw:
        raise ValidationError("A signature image is required.")
    if len(raw) > MAX_IMAGE_BYTES:
        raise ValidationError("The signature image is too large (200 KB maximum).")
    try:
        with Image.open(BytesIO(raw)) as probe:
            probe.verify()
        with Image.open(BytesIO(raw)) as image:
            if image.format != "PNG":
                raise ValidationError("The signature must be a PNG image.")
            width, height = image.size
            if width > MAX_WIDTH or height > MAX_HEIGHT:
                raise ValidationError("The signature image dimensions are too large.")
            rgba = image.convert("RGBA")
            flat = Image.alpha_composite(Image.new("RGBA", rgba.size, (255, 255, 255, 255)), rgba)
            rgb = flat.convert("RGB")
            if rgb.getextrema() == ((255, 255), (255, 255), (255, 255)):
                raise ValidationError("The signature is blank.")
    except ValidationError:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        raise ValidationError("The signature image is not a valid PNG.")
    return raw


@transaction.atomic
def add_record_signature(
    *, record_type, record_id, image, signer_name="", role_label="", captured_by=None
):
    entry = SIGNABLE_RECORDS.get(record_type)
    if entry is None:
        raise ValidationError("This record type cannot be signed.")
    signer_name = (signer_name or "").strip()
    role_label = (role_label or "").strip()
    if not signer_name:
        raise ValidationError("Enter the signer's name.")
    if len(signer_name) > MAX_SIGNER_NAME:
        raise ValidationError("The printed name is too long (150 characters maximum).")
    if len(role_label) > MAX_ROLE_LABEL:
        raise ValidationError("The role is too long (50 characters maximum).")
    try:
        record = entry.model.objects.get(pk=record_id)
    except entry.model.DoesNotExist:
        raise LookupError(f"{entry.label} record {record_id} does not exist.")
    png = validate_signature_png(image)
    number = getattr(record, entry.number_attr)
    signature = RecordSignature.objects.create(
        record_type=record_type,
        record_id=record.pk,
        record_number=number,
        signer_name=signer_name,
        role_label=role_label,
        image=png,
        captured_by=captured_by,
    )
    log_record_changes(
        record_type,
        record,
        number,
        {},
        {"Signature added": f"{signer_name or 'unnamed'} ({role_label or 'no role'})"},
        changed_by=captured_by,
    )
    return signature
