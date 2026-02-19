"""
Manual test script for comparison endpoint.
Run this to quickly verify the comparison feature works.

Usage:
    python test_comparison_manual.py
"""
import asyncio
import sys
from datetime import datetime
import uuid

# Add parent directory to path
sys.path.insert(0, '.')

from app.db.session import async_session
from app.models.calculation import Calculation
from app.models.user import User
from app.api.v1.endpoints.comparisons import compare_calculations
from app.schemas.comparison import ComparisonRequest


async def test_comparison():
    print("\n" + "="*60)
    print("COMPARISON ENDPOINT MANUAL TEST")
    print("="*60 + "\n")

    async with async_session() as db:
        # Create or get test user
        from sqlalchemy import select
        result = await db.execute(select(User).limit(1))
        test_user = result.scalar_one_or_none()

        if not test_user:
            print("ERROR: No users found in database. Please create a user first.")
            return

        print(f"Using test user: {test_user.email}\n")

        # Create 3 test calculations with different costs
        print("Creating 3 test calculations...")

        calc1 = Calculation(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            name="Cheap Option - China to USA",
            hs_code="8517120000",
            product_description="Mobile phones",
            origin_country="CN",
            destination_country="US",
            cif_value=5000.00,
            currency="USD",
            total_cost=5200.00,
            customs_duty=100.00,
            vat_amount=100.00,
            fta_eligible=False,
            result={"rates": {"mfn": 2.0, "vat": 2.0}},
            created_at=datetime.utcnow()
        )

        calc2 = Calculation(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            name="Expensive Option - China to EU",
            hs_code="8517120000",
            product_description="Mobile phones",
            origin_country="CN",
            destination_country="EU",
            cif_value=5000.00,
            currency="USD",
            total_cost=6000.00,
            customs_duty=300.00,
            vat_amount=700.00,
            fta_eligible=True,
            fta_savings=150.00,
            result={"rates": {"mfn": 6.0, "vat": 14.0}},
            created_at=datetime.utcnow()
        )

        calc3 = Calculation(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            name="Mid-Range Option - China to Japan",
            hs_code="8517120000",
            product_description="Mobile phones",
            origin_country="CN",
            destination_country="JP",
            cif_value=5000.00,
            currency="USD",
            total_cost=5500.00,
            customs_duty=200.00,
            vat_amount=300.00,
            fta_eligible=False,
            result={"rates": {"mfn": 4.0, "vat": 6.0}},
            created_at=datetime.utcnow()
        )

        db.add_all([calc1, calc2, calc3])
        await db.commit()

        print(f"  [OK] Created calculation 1: {calc1.name} - ${calc1.total_cost}")
        print(f"  [OK] Created calculation 2: {calc2.name} - ${calc2.total_cost}")
        print(f"  [OK] Created calculation 3: {calc3.name} - ${calc3.total_cost}\n")

        # Test comparison
        print("Testing comparison endpoint...")
        request = ComparisonRequest(
            calculation_ids=[calc1.id, calc2.id, calc3.id]
        )

        try:
            result = await compare_calculations(request, db, test_user)

            print("\n" + "="*60)
            print("COMPARISON RESULTS")
            print("="*60 + "\n")

            # Display metrics
            print("SUMMARY METRICS:")
            print(f"  Comparison Type: {result.metrics.comparison_type}")
            print(f"  Best Option:     ${result.metrics.min_total_cost:,.2f}")
            print(f"  Worst Option:    ${result.metrics.max_total_cost:,.2f}")
            print(f"  Average Cost:    ${result.metrics.avg_total_cost:,.2f}")
            print(f"  Cost Spread:     ${result.metrics.cost_spread:,.2f} ({result.metrics.cost_spread_percent:.1f}%)")
            print(f"  FTA Eligible:    {'Yes' if result.metrics.has_fta_eligible else 'No'}")
            if result.metrics.total_fta_savings:
                print(f"  FTA Savings:     ${result.metrics.total_fta_savings:,.2f}")
            print()

            # Display each calculation
            print("RANKED CALCULATIONS:")
            print("-" * 60)

            for calc in result.calculations:
                rank_symbol = "🥇" if calc.is_best else "🥉" if calc.is_worst else "🥈"
                print(f"\n{rank_symbol} RANK #{calc.rank}: {calc.name}")
                print(f"  Route:        {calc.origin_country} → {calc.destination_country}")
                print(f"  HS Code:      {calc.hs_code}")
                print(f"  Total Cost:   {calc.currency} ${calc.total_cost:,.2f}")
                print(f"  vs Average:   {calc.cost_vs_average_percent:+.1f}%")
                if calc.fta_eligible:
                    print(f"  FTA Status:   ✓ Eligible (Save ${calc.fta_savings:,.2f})")
                print("-" * 60)

            print("\n[SUCCESS] Comparison test passed! ✓\n")

            # Cleanup
            print("Cleaning up test data...")
            await db.delete(calc1)
            await db.delete(calc2)
            await db.delete(calc3)
            await db.commit()
            print("  [OK] Test calculations deleted\n")

        except Exception as e:
            print(f"\n[ERROR] Comparison test failed: {str(e)}\n")
            import traceback
            traceback.print_exc()

            # Cleanup on error
            try:
                await db.delete(calc1)
                await db.delete(calc2)
                await db.delete(calc3)
                await db.commit()
            except:
                pass


if __name__ == "__main__":
    asyncio.run(test_comparison())
