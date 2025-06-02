"""forms.py - Django form for handling refund requests."""
from datetime import datetime, date
import re
from django import forms
from django.core.exceptions import ValidationError

from .models import RefundRequest


class RefundForm(forms.ModelForm):
    """Form for handling refund requests."""

    class Meta:
        """Meta class for RefundForm."""
        model = RefundRequest
        fields = ['bank_name', 'account_number', 'card_number', 'expiry_date', 'cvv']
        widgets = {
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Bank of America',
                'maxlength': 100
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your bank account number',
                'maxlength': 50
            }),
            'card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '16-digit card number',
                'maxlength': 19
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'month'
            }, format='%Y-%m'),
            'cvv': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123',
                'maxlength': 4
            })
        }

    def clean_card_number(self):
        """Validate and clean card number."""
        card_number = self.cleaned_data.get('card_number', '').strip()

        # Remove spaces and non-digits
        digits_only = re.sub(r'\D', '', card_number)

        # Check length
        if len(digits_only) < 13 or len(digits_only) > 19:
            raise ValidationError("Card number must be between 13 and 19 digits.")

        # Basic Luhn algorithm check
        # if not self._luhn_check(digits_only):
        #     raise ValidationError("Invalid card number.")

        # Format with spaces (every 4 digits)
        formatted = ' '.join([digits_only[i:i+4] for i in range(0, len(digits_only), 4)])
        return formatted

    def clean_expiry_date(self):
        """Validate expiry date."""
        expiry_date = self.cleaned_data.get('expiry_date')

        if expiry_date:
            # Convert to string if it's a date object
            if isinstance(expiry_date, date):
                expiry_str = expiry_date.strftime('%Y-%m')
            else:
                expiry_str = str(expiry_date)

            try:
                expiry_datetime = datetime.strptime(expiry_str, '%Y-%m')
                current_date = datetime.now().replace(day=1)

                if expiry_datetime < current_date:
                    raise ValidationError("Card has expired.")

            except ValueError as exc:
                raise ValidationError("Invalid expiry date format.") from exc

        return expiry_date

    def clean_cvv(self):
        """Validate CVV."""
        cvv = self.cleaned_data.get('cvv', '').strip()

        if not re.match(r'^\d{3,4}$', cvv):
            raise ValidationError("CVV must be 3 or 4 digits.")

        return cvv

    def clean_account_number(self):
        """Validate account number."""
        account_number = self.cleaned_data.get('account_number', '').strip()

        if len(account_number) < 8:
            raise ValidationError("Account number must be at least 8 characters.")

        # Remove spaces and check if it contains only digits and hyphens
        cleaned = re.sub(r'[\s-]', '', account_number)
        if not re.match(r'^[0-9]+$', cleaned):
            raise ValidationError("Account number can only contain digits, spaces, and hyphens.")

        return account_number

    @staticmethod
    def _luhn_check(card_number):
        """Implement Luhn algorithm for basic card validation."""
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10 == 0
