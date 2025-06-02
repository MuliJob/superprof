"""Admin interface for managing refund requests."""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import RefundRequest

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    """Admin interface for RefundRequest model."""

    list_display = [
        'request_id_short', 'recipient_name', 'refund_amount', 
        'bank_name', 'masked_card', 'processed_status', 'created_at'
    ]
    list_filter = ['processed', 'created_at', 'bank_name']
    search_fields = ['request_id', 'recipient_name', 'bank_name']
    readonly_fields = [
        'request_id', 'created_at', 'updated_at', 'processed_at',
        'ip_address', 'user_agent', 'masked_card_display', 'masked_account_display'
    ]

    fieldsets = (
        ('Request Information', {
            'fields': ('request_id', 'recipient_name', 'refund_amount')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'masked_account_display')
        }),
        ('Card Details', {
            'fields': ('card_number', 'masked_card_display', 'expiry_date', 'cvv')
        }),
        ('Processing Status', {
            'fields': ('processed', 'processed_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        })
    )

    actions = ['mark_as_processed']

    def request_id_short(self, obj):
        """Display shortened request ID."""
        return str(obj.request_id)[:8] + '...'
    request_id_short.short_description = 'Request ID'

    def masked_card(self, obj):
        """Display masked card number."""
        return obj.get_masked_card_number()
    masked_card.short_description = 'Card Number'

    def masked_card_display(self, obj):
        """Display masked card number in detail view."""
        return obj.get_masked_card_number()
    masked_card_display.short_description = 'Masked Card Number'

    def masked_account_display(self, obj):
        """Display masked account number in detail view."""
        return obj.get_masked_account_number()
    masked_account_display.short_description = 'Masked Account Number'

    def processed_status(self, obj):
        """Display processing status with color."""
        if obj.processed:
            return format_html('<span style="color: green;">✓ Processed</span>')
        return format_html('<span style="color: red;">✗ Pending</span>')
    processed_status.short_description = 'Status'

    def mark_as_processed(self, request, queryset):
        """Action to mark selected requests as processed."""
        updated = queryset.update(processed=True, processed_at=timezone.now())
        self.message_user(request, f'{updated} refund requests marked as processed.')
    mark_as_processed.short_description = 'Mark selected as processed'
