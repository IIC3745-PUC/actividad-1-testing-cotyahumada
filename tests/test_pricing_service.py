import unittest
from unittest.mock import Mock, patch

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):

	def setUp(self):
		self.ps = PricingService()

	def test_Coupon_Empty(self):
		self.assertEqual(self.ps.apply_coupon(10000, None), 10000)

	def test_Coupon_Save10(self):
		self.assertEqual(self.ps.apply_coupon(10000, "SAVE10"), 9000)

	def test_Coupon_CLP2000(self):
		self.assertEqual(self.ps.apply_coupon(10000, "CLP2000"), 8000)
	
	def test_Coupon_Invalid(self):
		with self.assertRaises(PricingError):
			self.ps.apply_coupon(10000, "INVALID")
	
	# tests para tax_cents
	def test_Tax_CL(self):
		self.assertEqual(self.ps.tax_cents(10000, "CL"), 1900)
	
	def test_Tax_EU(self):
		self.assertEqual(self.ps.tax_cents(10000, "EU"), 2100)

	def test_Tax_US(self):
		self.assertEqual(self.ps.tax_cents(10000, "US"), 0)
	
	def test_Tax_UnsupportedCountry(self):
		with self.assertRaises(PricingError):
			self.ps.tax_cents(10000, "XX")

	# tests para shipping_cents
	
	def test_Shipping_CL_Free(self):
		self.assertEqual(self.ps.shipping_cents(20000, "CL"), 0)
	
	def test_Shipping_CL_Paid(self):
		self.assertEqual(self.ps.shipping_cents(10000, "CL"), 2500)

	def test_Shipping_US(self):
		self.assertEqual(self.ps.shipping_cents(10000, "US"), 5000)
	
	def test_Shipping_EU(self):
		self.assertEqual(self.ps.shipping_cents(10000, "EU"), 5000)
	
	def test_Shipping_UnsupportedCountry(self):
		with self.assertRaises(PricingError):
			self.ps.shipping_cents(10000, "XX")

	# tests para subtotal_cents
	def test_Subtotal_Valid(self):
		items = [CartItem("sku", qty=2, unit_price_cents=1000), CartItem("sku", qty=1, unit_price_cents=500)]
		self.assertEqual(self.ps.subtotal_cents(items), 2500)
	
	def test_Subtotal_Qty(self):
		items = [CartItem("sku", qty=0, unit_price_cents=1000), CartItem("sku", qty=1, unit_price_cents=500)]
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents(items)
	
	def test_Subtotal_UnitPrice(self):
		items = [CartItem("sku", qty=2, unit_price_cents=-1000), CartItem("sku", qty=1, unit_price_cents=500)]
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents(items)

	def test_TotalCents(self):
		items = [CartItem("sku", qty=2, unit_price_cents=1000), CartItem("sku", qty=1, unit_price_cents=500)]
		with patch.object(self.ps, "subtotal_cents", return_value=2500), \
			 patch.object(self.ps, "apply_coupon", return_value=2250), \
			 patch.object(self.ps, "tax_cents", return_value=427), \
			 patch.object(self.ps, "shipping_cents", return_value=2500):
			
			total = self.ps.total_cents(items, "SAVE10", "CL")
			self.assertEqual(total, 2250 + 427 + 2500)


def runTests(testClass):
  # Add tests from the test class
  loader = unittest.TestLoader()
  suite = loader.loadTestsFromTestCase(testClass)
  # Run the test suite
  runner = unittest.TextTestRunner()
  runner.run(suite)

runTests(TestPricingService)


