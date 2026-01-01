"""
Currency conversion module with intuitive syntax.

Usage:
    from currencyconsts import *
    
    # Simple conversions (from USD by default)
    100 * EUR  # Convert $100 to EUR
    50 * GBP   # Convert $50 to GBP
    
    # Change base currency
    set_base('EUR')
    100 * USD  # Convert €100 to USD
    
    # Apply margin (like PayPal's ~3-4%)
    set_margin(3.5)  # 3.5% markup
    
    # Get rate info
    eur.rate       # Current EUR rate
    eur.inverse    # Inverse rate (1/rate)
"""

import requests
from datetime import datetime, timedelta
from typing import Union
import threading

# ============================================================================
# Configuration
# ============================================================================

_config = {
    'base_currency': 'usd',
    'margin_percent': 0,  # Markup percentage (e.g., 3.5 for PayPal-like rates)
    'cache_ttl_minutes': 60,
    'offline_mode': False,  # Force use of fallback rates
    'api_endpoints': [
        # ExchangeRate-API Open Access (no key required)
        'https://open.er-api.com/v6/latest/{BASE}',
    ],
}

_cache = {
    'rates': {},
    'last_fetch': None,
    'base': None,
    'using_fallback': False,
}

_lock = threading.Lock()


# ============================================================================
# API Functions
# ============================================================================

def _parse_api_response(data: dict, base: str, url: str) -> dict:
    """Parse response from different API formats."""
    base_lower = base.lower()
    base_upper = base.upper()
    
    # Format 1: ExchangeRate-API format {"rates": {...}}
    if 'rates' in data:
        return {k.upper(): v for k, v in data['rates'].items()}
    
    # Format 2: Fawazahmed0 format {"usd": {...}}
    if base_lower in data:
        return {k.upper(): v for k, v in data[base_lower].items()}
    
    # Format 3: Direct rates dict
    if isinstance(data, dict) and all(isinstance(v, (int, float)) for v in data.values()):
        return {k.upper(): v for k, v in data.items()}
    
    return {}


def _fetch_rates(base: str) -> dict:
    """Fetch exchange rates from multiple API sources with fallback."""
    base_lower = base.lower()
    base_upper = base.upper()    
    errors = []
    
    # Try each API endpoint
    for endpoint_template in _config['api_endpoints']:
        try:
            # Handle different URL formats
            url = endpoint_template.format(base=base_lower, BASE=base_upper)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            rates = _parse_api_response(data, base_lower, url)
            if rates:
                return rates
                
        except Exception as e:
            errors.append(f"{endpoint_template}: {e}")
            continue
    
    raise ConnectionError(f"Could not fetch live rates from any API. Errors: {errors}")


def _get_rates() -> dict:
    """Get rates with caching."""
    with _lock:
        now = datetime.now()
        base = _config['base_currency']
        
        # Check if cache is valid
        if (_cache['rates'] 
            and _cache['base'] == base
            and _cache['last_fetch'] 
            and (now - _cache['last_fetch']) < timedelta(minutes=_config['cache_ttl_minutes'])):
            return _cache['rates']
        
        # Fetch fresh rates
        rates = _fetch_rates(base)
        _cache['rates'] = rates
        _cache['last_fetch'] = now
        _cache['base'] = base
        
        return rates


def refresh_rates():
    """Force refresh of exchange rates."""
    with _lock:
        _cache['rates'] = {}
        _cache['last_fetch'] = None
    _get_rates()


# ============================================================================
# Configuration Functions
# ============================================================================

def set_base(currency: str):
    """
    Set the base currency for conversions.
    
    Args:
        currency: Currency code (e.g., 'USD', 'EUR', 'GBP')
    
    Example:
        set_base('EUR')
        100 * usd  # Convert €100 to USD
    """
    with _lock:
        _config['base_currency'] = currency.upper()
        _cache['rates'] = {}  # Invalidate cache
        _cache['last_fetch'] = None


def set_margin(percent: float):
    """
    Set a margin/markup percentage on conversions.
    
    This simulates fees that services like PayPal add (~3-4%).
    
    Args:
        percent: Margin percentage (e.g., 3.5 for 3.5% markup)
    
    Example:
        set_margin(3.5)  # Apply 3.5% markup like PayPal
        100 * eur  # Will give slightly less EUR
    """
    _config['margin_percent'] = percent


def set_cache_ttl(minutes: int):
    """Set how long rates are cached before refresh."""
    _config['cache_ttl_minutes'] = minutes


# ============================================================================
# Currency Class
# ============================================================================

class Currency:
    """
    Currency object that enables intuitive conversion syntax.
    
    Supports multiplication with numbers for conversion:
        100 * eur  -> Converts 100 of base currency to EUR
        eur * 100  -> Same thing
    """
    
    def __init__(self, code: str):
        self.code = code.upper()
    
    @property
    def rate(self) -> float:
        """Get the current exchange rate from base currency."""
        rates = _get_rates()
        rate = rates.get(self.code)
        if rate is None:
            raise ValueError(f"Currency '{self.code}' not found")
        return rate
    
    @property
    def rate_with_margin(self) -> float:
        """Get rate with margin applied (simulates service fees)."""
        base_rate = self.rate
        margin = _config['margin_percent']
        # Margin reduces what you get (like PayPal)
        return base_rate * (1 - margin / 100)
        
    def __repr__(self):
        try:
            return f"<{self.code}: 1 {_config['base_currency'].upper()} = {self.rate:.6f} {self.code}>"
        except:
            return f"<Currency: {self.code.upper()}>"
    
    def __rmul__(self, amount: Union[int, float]) -> float:
        """Enable: 100 * eur"""
        return self._convert(amount)
    
    def __mul__(self, amount: Union[int, float]) -> float:
        """Enable: eur * 100"""
        return self._convert(amount)
    
    def __truediv__(self, amount: Union[int, float]) -> float:
        """Enable: eur / 100"""
        return self._convert(1 / amount)
    
    def __rtruediv__(self, amount: Union[int, float]) -> float:
        """Enable: 100 / eur"""
        return amount / self.rate
    
    def __floordiv__(self, amount: Union[int, float]) -> float:
        """Enable: eur // 100"""
        return self._convert(1) // amount
    
    def __rfloordiv__(self, amount: Union[int, float]) -> float:
        """Enable: 100 // eur"""
        return amount // self._convert(1)
    
    def __add__(self, amount: Union[int, float]) -> float:
        """Enable: eur + 100"""
        return self._convert(1) + amount
    
    def __radd__(self, amount: Union[int, float]) -> float:
        """Enable: 100 + eur"""
        return amount + self._convert(1)
    
    def __sub__(self, amount: Union[int, float]) -> float:
        """Enable: eur - 100"""
        return self._convert(1) - amount
    
    def __rsub__(self, amount: Union[int, float]) -> float:
        """Enable: 100 - eur"""
        return amount - self._convert(1)
    
    def __mod__(self, amount: Union[int, float]) -> float:
        """Enable: eur % 100"""
        return self._convert(1) % amount
    
    def __rmod__(self, amount: Union[int, float]) -> float:
        """Enable: 100 % eur"""
        return amount % self._convert(1)
    
    def _convert(self, amount: Union[int, float]) -> float:
        """Perform the conversion."""
        rate = self.rate_with_margin if _config['margin_percent'] > 0 else self.rate
        converted = amount * rate
        return converted

# ============================================================================
# Currency Constants - Dynamically Generated
# ============================================================================

CURRENCY_CODES = [
    # Major World Currencies
    'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'CHF', 'AUD', 'CAD', 'NZD', 'HKD', 'SGD',
    # European Currencies
    'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'RON', 'BGN', 'HRK', 'RSD', 'ISK', 'RUB', 'UAH', 'TRY',
    # Asian Currencies
    'INR', 'KRW', 'THB', 'MYR', 'IDR', 'PHP', 'VND', 'TWD', 'PKR', 'BDT', 'LKR', 'NPR', 'MMK', 'KHR',
    # Middle East & Africa
    'AED', 'SAR', 'ILS', 'EGP', 'ZAR', 'NGN', 'KES', 'GHS', 'MAD', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD',
    # Americas
    'MXN', 'BRL', 'ARS', 'CLP', 'COP', 'PEN', 'UYU',
]

# Dynamically create currency constants
for code in CURRENCY_CODES:
    globals()[code] = Currency(code)
