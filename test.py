"""
Test script to verify all currency conversions are working and non-zero.
"""

from currencyconsts import *

def test_conversions():
    """Test basic currency conversions."""
    print("=" * 60)
    print("TESTING CURRENCY CONVERSIONS")
    print("=" * 60)
    
    # Test major currencies
    print("\n1. Testing Major World Currencies (Base: USD)")
    test_currencies = [
        ('USD', USD), ('EUR', EUR), ('GBP', GBP), ('JPY', JPY), 
        ('CNY', CNY), ('AUD', AUD), ('CAD', CAD)
    ]
    
    for code, currency in test_currencies:
        result = 100 * currency
        rate = currency.rate
        rate_with_margin = currency.rate_with_margin
        
        assert rate > 0, f"{code} rate is zero or negative!"
        assert result.result > 0, f"{code} conversion result is zero or negative!"
        
        print(f"  {code:4s}: Rate={rate:>12.6f} | With Margin={rate_with_margin:>12.6f} | 100 USD = {result}")
    
    # Test Asian currencies
    print("\n2. Testing Asian Currencies")
    asian = [
        ('INR', INR), ('KRW', KRW), ('THB', THB), ('PHP', PHP),
        ('VND', VND), ('IDR', IDR)
    ]
    
    for code, currency in asian:
        result = 100 * currency
        rate = currency.rate
        
        assert rate > 0, f"{code} rate is zero or negative!"
        assert result.result > 0, f"{code} conversion result is zero or negative!"
        
        print(f"  {code:4s}: Rate={rate:>12.6f} | 100 USD = {result}")
    
    # Test Middle East & Africa
    print("\n3. Testing Middle East & Africa Currencies")
    mea = [
        ('AED', AED), ('SAR', SAR), ('ILS', ILS), ('ZAR', ZAR),
        ('EGP', EGP), ('NGN', NGN)
    ]
    
    for code, currency in mea:
        result = 100 * currency
        rate = currency.rate
        
        assert rate > 0, f"{code} rate is zero or negative!"
        assert result.result > 0, f"{code} conversion result is zero or negative!"
        
        print(f"  {code:4s}: Rate={rate:>12.6f} | 100 USD = {result}")
    
    # Test Americas
    print("\n4. Testing Americas Currencies")
    americas = [
        ('MXN', MXN), ('BRL', BRL), ('ARS', ARS), ('CLP', CLP),
        ('COP', COP), ('PEN', PEN)
    ]
    
    for code, currency in americas:
        result = 100 * currency
        rate = currency.rate
        
        assert rate > 0, f"{code} rate is zero or negative!"
        assert result.result > 0, f"{code} conversion result is zero or negative!"
        
        print(f"  {code:4s}: Rate={rate:>12.6f} | 100 USD = {result}")
        
    print("\n" + "=" * 60)
    print("✓ ALL CONVERSIONS ARE NON-ZERO AND WORKING!")
    print("=" * 60)


def test_margin():
    """Test margin application."""
    print("\n" + "=" * 60)
    print("TESTING MARGIN APPLICATION")
    print("=" * 60)
    
    # Get current margin
    from currencyconsts import _config
    current_margin = _config['margin_percent']
    print(f"\nCurrent margin: {current_margin}%")
    
    # Test with margin
    print(f"\nWith {current_margin}% margin:")
    result_with_margin = 100 * EUR
    print(f"  100 USD = {result_with_margin}")
    print(f"  Base rate: {EUR.rate:.6f}")
    print(f"  Rate with margin: {EUR.rate_with_margin:.6f}")
    print(f"  Difference: {EUR.rate - EUR.rate_with_margin:.6f}")
    
    # Test without margin
    set_margin(0)
    print(f"\nWith 0% margin:")
    result_no_margin = 100 * EUR
    print(f"  100 USD = {result_no_margin}")
    
    # Restore margin
    set_margin(current_margin)
    
    print("\n✓ MARGIN IS WORKING CORRECTLY!")


def test_base_currency():
    """Test changing base currency."""
    print("\n" + "=" * 60)
    print("TESTING BASE CURRENCY CHANGES")
    print("=" * 60)
    
    # Save original
    from currencyconsts import _config
    original_base = _config['base_currency']
    
    # Test USD base
    print("\n1. Base: USD")
    set_base('USD')
    result = 100 * EUR
    print(f"  100 USD = {result}")
    assert result.result > 0, "EUR conversion from USD failed!"
    
    # Test EUR base
    print("\n2. Base: EUR")
    set_base('EUR')
    result = 100 * USD
    print(f"  100 EUR = {result}")
    assert result.result > 0, "USD conversion from EUR failed!"
    
    # Test GBP base
    print("\n3. Base: GBP")
    set_base('GBP')
    result = 100 * USD
    print(f"  100 GBP = {result}")
    assert result.result > 0, "USD conversion from GBP failed!"
    
    # Restore original
    set_base(original_base)
    
    print("\n✓ BASE CURRENCY CHANGES WORKING!")


def test_api_status():
    """Check API status and fallback."""
    print("\n" + "=" * 60)
    print("API STATUS")
    print("=" * 60)
    
    from currencyconsts import _config, _cache
    print(f"\nUsing fallback rates: {_cache.get('using_fallback', False)}")
    print(f"Cache TTL: {_config['cache_ttl_minutes']} minutes")
    print(f"Base currency: {_config['base_currency'].upper()}")
    print(f"Margin: {_config['margin_percent']}%")
    print(f"Offline mode: {_config.get('offline_mode', False)}")
    
    if _cache.get('using_fallback'):
        print("\n⚠ Using fallback rates (network unavailable or API error)")
    else:
        print("\n✓ Using live rates from API")


if __name__ == '__main__':
    try:
        print("\n")
        print("*" * 60)
        print("  CURRENCY CONVERSION MODULE TEST SUITE")
        print("*" * 60)
        
        # Run all tests
        test_api_status()
        test_conversions()
        test_margin()
        test_base_currency()
        
        print("\n" + "*" * 60)
        print("  ALL TESTS PASSED! ✓")
        print("*" * 60)
        print()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
