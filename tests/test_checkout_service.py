import unittest
from unittest.mock import Mock, patch

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	
	def setUp(self):
		self.payments = Mock()
		self.email = Mock()
		self.fraud = Mock(
			score=Mock(return_value=50)
		)
		self.repo = Mock()
		self.pricing = Mock(
			total_cents=Mock(return_value=20000),
			apply_coupon=Mock(return_value=18000),
			tax_cents=Mock(return_value=1900),
			shipping_cents=Mock(return_value=2500),
		)

		self.pricing.total_cents.return_value = 20000
		self.fraud.score.return_value = 50
		self.payments.charge.return_value = ChargeResult(ok=True, charge_id="charge123")

		self.service = CheckoutService(
            payments=self.payments,
            email=self.email,
            fraud=self.fraud,
            repo=self.repo,
            pricing=self.pricing,
        )

		self.items = [CartItem("SKU1", 10000, 2)]

			
	def test_InvalidUser(self):
		result = self.service.checkout(user_id="", items=self.items, payment_token="token", country="CL", coupon_code=None)
		self.assertEqual(result, "INVALID_USER")

	def test_PricingError(self):
		# Simulamos un error en el cálculo del precio total, con Mock para no depender de pricing
		self.pricing.total_cents.side_effect = PricingError("Pricing failed")
		# items = [CartItem("SKU1", 10000, 0)]
		result = self.service.checkout(user_id="user1", items=self.items, payment_token="token", country="CL", coupon_code=None)
		self.assertEqual(result, "INVALID_CART:Pricing failed")
	
	def test_FraudRejection(self):
		self.pricing.total_cents.return_value = 20000
		self.fraud.score.return_value = 85
		result = self.service.checkout(user_id="user1", items=self.items, payment_token="token", country="CL", coupon_code=None)
		self.assertEqual(result, "REJECTED_FRAUD")
	
	def test_PaymentFailed(self):
		# no dependemos de nada mas, solo del resultado del pago
		self.pricing.total_cents.return_value = 20000
		self.fraud.score.return_value = 10
		self.payments.charge.return_value = ChargeResult(ok=False, charge_id=None, reason="Card declined")
		result = self.service.checkout(user_id="user1", items=self.items, payment_token="token", country="CL", coupon_code=None)
		self.assertEqual(result, "PAYMENT_FAILED:Card declined")
	
	
	def test_SuccessfulCheckout(self):
		self.pricing.total_cents.return_value = 20000
		self.fraud.score.return_value = 10
		with patch("src.checkout.uuid.uuid4", return_value="fixed-uuid"):
			self.payments.charge.return_value = ChargeResult(ok=True, charge_id="charge123", reason=None)
			result = self.service.checkout(user_id="user1", items=self.items, payment_token="token", country="CL", coupon_code=None)

			self.assertEqual("OK:fixed-uuid", result)
			
	



	

def runTests(testClass):
  # Add tests from the test class
  loader = unittest.TestLoader()
  suite = loader.loadTestsFromTestCase(testClass)
  # Run the test suite
  runner = unittest.TextTestRunner()
  runner.run(suite)

runTests(TestCheckoutService)
	
