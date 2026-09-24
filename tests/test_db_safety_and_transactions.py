from __future__ import annotations

import unittest
from app_factory import create_app
from config import Config
from models import db
from models.admin import BlacklistedDomain
from models.product_db import Product, ProductIdentifier, ProductAttribute, Ingredient, ProductIngredient
from routes.admin import _generate_product_id


class DBSafetyTestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class TestDBSafetyAndTransactions(unittest.TestCase):
    def setUp(self):
        self.app = create_app(DBSafetyTestConfig)
        self.client = self.app.test_client()

    def test_schema_drift_does_not_drop_tables(self):
        from database.init_db import _verify_schema
        with self.app.app_context():
            # Add an extra column to blacklisted_domains
            with db.engine.begin() as conn:
                conn.execute(db.text("ALTER TABLE blacklisted_domains ADD COLUMN extra_test_col TEXT"))
            # Insert a record
            b = BlacklistedDomain(domain="test-keep.com", reason="testing")
            db.session.add(b)
            db.session.commit()

            # Run schema verification
            _verify_schema(self.app)

            # Ensure table still exists and data was not dropped
            saved = BlacklistedDomain.query.filter_by(domain="test-keep.com").first()
            self.assertIsNotNone(saved)

    def test_product_id_generation_is_unique(self):
        with self.app.app_context():
            id1 = _generate_product_id("Acme", "Super Soap")
            id2 = _generate_product_id("Acme", "Super Soap")
            self.assertNotEqual(id1, id2)
            self.assertTrue(id1.startswith("PRD-ACMESUPERSOAP"))
            self.assertTrue(id2.startswith("PRD-ACMESUPERSOAP"))

    def test_product_cascade_deletion(self):
        with self.app.app_context():
            prod_id = _generate_product_id("CascadeBrand", "CascadeProd")
            product = Product(
                product_id=prod_id,
                brand_name="CascadeBrand",
                product_name="CascadeProd",
            )
            db.session.add(product)
            db.session.flush()

            identifier = ProductIdentifier(
                product_id=prod_id,
                identifier_type="barcode",
                identifier_value="999888777",
            )
            db.session.add(identifier)

            attr = ProductAttribute(
                product_id=prod_id,
                attribute_name="color",
                attribute_value="blue",
            )
            db.session.add(attr)
            db.session.commit()

            self.assertEqual(ProductIdentifier.query.filter_by(product_id=prod_id).count(), 1)
            self.assertEqual(ProductAttribute.query.filter_by(product_id=prod_id).count(), 1)

            # Delete product
            db.session.delete(product)
            db.session.commit()

            # Check that child records were cascaded
            self.assertEqual(ProductIdentifier.query.filter_by(product_id=prod_id).count(), 0)
            self.assertEqual(ProductAttribute.query.filter_by(product_id=prod_id).count(), 0)


if __name__ == "__main__":
    unittest.main()

