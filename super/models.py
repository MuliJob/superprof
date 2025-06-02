"""Models for handling refund requests in a Django application."""
import uuid
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

class RefundRequest(models.Model):
    """Model to store refund request data."""

    # Unique identifier for each refund request
    request_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for this refund request"
    )

    # Personal Information
    recipient_name = models.CharField(
        max_length=100,
        default="customer",
        help_text="Name of the person receiving the refund"
    )

    refund_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100.00,
        help_text="Amount to be refunded"
    )

    # Bank Information
    bank_name = models.CharField(
        max_length=100,
        help_text="Name of the bank"
    )

    account_number = models.CharField(
        max_length=50,
        validators=[
            MinLengthValidator(8, "Account number must be at least 8 characters"),
            MaxLengthValidator(50, "Account number cannot exceed 50 characters")
        ],
        help_text="Bank account number"
    )

    # Card Information
    card_number = models.CharField(
        max_length=19,  # 16 digits + 3 spaces
        validators=[
            RegexValidator(
                regex=r'^[\d\s]{13,19}$',
                message="Card number must be 13-19 characters (digits and spaces only)"
            )
        ],
        help_text="Credit/Debit card number"
    )

    expiry_date = models.CharField(
        max_length=7,  # YYYY-MM format
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{2}$',
                message="Expiry date must be in YYYY-MM format"
            )
        ],
        help_text="Card expiry date in YYYY-MM format"
    )

    cvv = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r'^\d{3,4}$',
                message="CVV must be 3 or 4 digits"
            )
        ],
        help_text="Card CVV/CVC code"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the refund request was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the refund request was last updated"
    )

    processed = models.BooleanField(
        default=False,
        help_text="Whether the refund has been processed"
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the refund was processed"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the requester"
    )

    user_agent = models.TextField(
        blank=True,
        help_text="User agent string of the requester"
    )

    objects = models.Manager()
    class Meta:
        """Meta options for the RefundRequest model."""
        db_table = 'refund_requests'
        verbose_name = 'Refund Request'
        verbose_name_plural = 'Refund Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund Request {self.request_id} - {self.recipient_name} - ${self.refund_amount}"

    def get_masked_card_number(self):
        """Return masked card number for security."""
        card_number_str = str(self.card_number)
        if len(card_number_str) >= 4:
            return "**** **** **** " + card_number_str[-4:]
        return "****"

    def get_masked_account_number(self):
        """Return masked account number for security."""
        account_number_str = str(self.account_number)
        if len(account_number_str) >= 4:
            return "*" * (len(account_number_str) - 4) + account_number_str[-4:]
        return "****"

    def mark_as_processed(self):
        """Mark the refund request as processed."""
        self.processed = True
        self.processed_at = timezone.now()
        self.save()
