"""
Tests for comparison endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.models.calculation import Calculation


@pytest.mark.asyncio
async def test_compare_calculations_success(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
    auth_headers
):
    """Test successful comparison of 3 calculations"""
    # Create 3 test calculations with different costs
    calc1 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="US",
        cif_value=5000.00,
        currency="USD",
        total_cost=5200.00,
        customs_duty=100.00,
        vat_amount=100.00,
        fta_eligible=False,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )
    calc2 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="EU",
        cif_value=5000.00,
        currency="USD",
        total_cost=6000.00,
        customs_duty=300.00,
        vat_amount=700.00,
        fta_eligible=True,
        fta_savings=150.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )
    calc3 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="JP",
        cif_value=5000.00,
        currency="USD",
        total_cost=5500.00,
        customs_duty=200.00,
        vat_amount=300.00,
        fta_eligible=False,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )

    db_session.add_all([calc1, calc2, calc3])
    await db_session.commit()

    # Test comparison
    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": [calc1.id, calc2.id, calc3.id]},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert len(data['calculations']) == 3
    assert data['total_compared'] == 3
    assert 'metrics' in data
    assert 'comparison_date' in data

    # Verify metrics
    metrics = data['metrics']
    assert metrics['min_total_cost'] == 5200.00  # calc1
    assert metrics['max_total_cost'] == 6000.00  # calc2
    assert metrics['avg_total_cost'] == 5566.67  # approximate
    assert metrics['cost_spread'] == 800.00  # 6000 - 5200
    assert metrics['comparison_type'] == 'same_hs_different_countries'
    assert metrics['has_fta_eligible'] is True

    # Verify rankings
    calcs = {c['id']: c for c in data['calculations']}
    assert calcs[calc1.id]['rank'] == 1  # Lowest cost
    assert calcs[calc1.id]['is_best'] is True
    assert calcs[calc2.id]['rank'] == 3  # Highest cost
    assert calcs[calc2.id]['is_worst'] is True
    assert calcs[calc3.id]['rank'] == 2  # Middle


@pytest.mark.asyncio
async def test_compare_validation_min_2(client: AsyncClient, auth_headers):
    """Test validation: requires at least 2 calculations"""
    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": ["calc-1"]},
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_compare_validation_max_5(client: AsyncClient, auth_headers):
    """Test validation: maximum 5 calculations"""
    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": ["1", "2", "3", "4", "5", "6"]},
        headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_compare_validation_duplicates(client: AsyncClient, auth_headers):
    """Test validation: no duplicate IDs allowed"""
    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": ["calc-1", "calc-1", "calc-2"]},
        headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_compare_unauthorized_calculations(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
    auth_headers
):
    """Test cannot compare other user's calculations"""
    # Create calculation for another user
    other_user_id = str(uuid.uuid4())
    other_calc = Calculation(
        id=str(uuid.uuid4()),
        user_id=other_user_id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="US",
        cif_value=5000.00,
        currency="USD",
        total_cost=5200.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )

    my_calc = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="US",
        cif_value=5000.00,
        currency="USD",
        total_cost=5200.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )

    db_session.add_all([other_calc, my_calc])
    await db_session.commit()

    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": [other_calc.id, my_calc.id]},
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_compare_different_hs_same_country(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
    auth_headers
):
    """Test comparison type detection: different HS codes, same country"""
    calc1 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="US",
        cif_value=5000.00,
        currency="USD",
        total_cost=5200.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )
    calc2 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8703230010",
        origin_country="CN",
        destination_country="US",
        cif_value=50000.00,
        currency="USD",
        total_cost=52000.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )

    db_session.add_all([calc1, calc2])
    await db_session.commit()

    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": [calc1.id, calc2.id]},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data['metrics']['comparison_type'] == 'different_hs_same_country'


@pytest.mark.asyncio
async def test_compare_cost_vs_average_calculation(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
    auth_headers
):
    """Test that cost_vs_average is calculated correctly"""
    # Create 3 calculations: 1000, 2000, 3000
    # Average should be 2000
    # Differences: -1000 (-50%), 0 (0%), +1000 (+50%)

    calc1 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="US",
        cif_value=1000.00,
        currency="USD",
        total_cost=1000.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )
    calc2 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="EU",
        cif_value=2000.00,
        currency="USD",
        total_cost=2000.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )
    calc3 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        hs_code="8517120000",
        origin_country="CN",
        destination_country="JP",
        cif_value=3000.00,
        currency="USD",
        total_cost=3000.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )

    db_session.add_all([calc1, calc2, calc3])
    await db_session.commit()

    response = await client.post(
        "/api/v1/comparisons/compare",
        json={"calculation_ids": [calc1.id, calc2.id, calc3.id]},
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    calcs = {c['id']: c for c in data['calculations']}

    # Check percentages (allowing small floating point errors)
    assert abs(calcs[calc1.id]['cost_vs_average_percent'] - (-50.0)) < 0.1
    assert abs(calcs[calc2.id]['cost_vs_average_percent'] - 0.0) < 0.1
    assert abs(calcs[calc3.id]['cost_vs_average_percent'] - 50.0) < 0.1


@pytest.mark.asyncio
async def test_export_comparison_csv(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user,
    auth_headers
):
    """Test CSV export for comparison"""
    # Create 2 test calculations
    calc1 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Calculation A",
        hs_code="8517120000",
        origin_country="CN",
        destination_country="US",
        cif_value=5000.00,
        currency="USD",
        total_cost=5200.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )
    calc2 = Calculation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        name="Calculation B",
        hs_code="8517120000",
        origin_country="CN",
        destination_country="EU",
        cif_value=5000.00,
        currency="USD",
        total_cost=6000.00,
        result={"test": "data"},
        created_at=datetime.utcnow()
    )

    db_session.add_all([calc1, calc2])
    await db_session.commit()

    response = await client.post(
        "/api/v1/export/comparison/csv",
        json={"calculation_ids": [calc1.id, calc2.id]},
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers['content-type'] == 'text/csv; charset=utf-8'
    assert 'comparison_export_' in response.headers['content-disposition']

    # Verify CSV content
    csv_content = response.text
    assert 'Metric' in csv_content
    assert 'Calculation A' in csv_content
    assert 'Calculation B' in csv_content
    assert 'HS Code' in csv_content
    assert 'TOTAL COST' in csv_content
