# Python Currency Conversion Constants

## Usage

Download and locally pip install via

```bash
pip install -e .
```

```python
>>> from currencyconsts import *

>>> # Convert USD to EUR
>>> 100 * EUR
85.16

>>> # Convert EUR to USD
>>> 100 / EUR
117.42

>>> CURRENCY_CODES
['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'CHF', 'AUD', 'CAD', 'NZD', 'HKD', 'SGD', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK', 'RSD', 'ISK', 'RUB', 'UAH', 'TRY', 'INR', 'KRW', 'THB', 'MYR', 'IDR', 'PHP', 'VND', 'TWD', 'PKR', 'BDT', 'LKR', 'NPR', 'MMK', 'KHR', 'AED', 'SAR', 'ILS', 'EGP', 'ZAR', 'NGN', 'KES', 'GHS', 'MAD', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD', 'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN', 'UYU']
```