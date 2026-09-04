"""
Forecasting and Business Projections services.
Provides linear trend analysis for revenues, collections, and customer growths.
"""
from datetime import datetime, timedelta
import decimal
from database import db

def calculate_trend(data_points):
    """
    Computes a simple linear trend forecast (y = mx + c) from historical values list.
    Returns the projected next value.
    """
    n = len(data_points)
    if n < 2:
        return float(data_points[0]) if n == 1 else 0.0
        
    x = list(range(n))
    y = [float(val) for val in data_points]
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xx = sum(i*i for i in x)
    sum_xy = sum(i*j for i, j in zip(x, y))
    
    denom = (n * sum_xx - sum_x * sum_x)
    if denom == 0:
        return y[-1]
        
    m = (n * sum_xy - sum_x * sum_y) / denom
    c = (sum_y - m * sum_x) / n
    
    # Project next point (index n)
    next_val = m * n + c
    return max(0.0, next_val)


def forecast_monthly_revenue():
    """
    Projects next month's total revenue collections using a 3-month history.
    """
    from models.payment import Payment
    today = datetime.utcnow()
    
    # Get revenue collected in the last 3 months
    revenue_history = []
    for i in range(3, 0, -1):
        m_start = (today - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0)
        m_end = (m_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        m_val = db.session.query(db.func.sum(Payment.payment_amount)).filter(
            Payment.payment_date >= m_start,
            Payment.payment_date <= m_end,
            Payment.payment_status == 'paid'
        ).scalar() or 0
        revenue_history.append(m_val)
        
    return calculate_trend(revenue_history)


def forecast_monthly_collections():
    """
    Forecasts upcoming collections based on instalment schedule rows due in the next 30 days.
    """
    from models.instalment_schedule import InstalmentSchedule
    today = datetime.utcnow()
    thirty_days_later = today + timedelta(days=30)
    
    expected_sum = db.session.query(db.func.sum(InstalmentSchedule.balance)).filter(
        InstalmentSchedule.payment_status.in_(['pending', 'overdue']),
        InstalmentSchedule.due_date >= today,
        InstalmentSchedule.due_date <= thirty_days_later
    ).scalar() or 0
    
    return float(expected_sum)


def forecast_customer_growth():
    """
    Projects customer registrations for the next month using customer monthly registration rates.
    """
    from models.customer import Customer
    today = datetime.utcnow()
    
    growth_history = []
    for i in range(3, 0, -1):
        m_start = (today - timedelta(days=i * 30)).replace(day=1, hour=0, minute=0, second=0)
        m_end = (m_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        m_count = Customer.query.filter(
            Customer.created_at >= m_start,
            Customer.created_at <= m_end,
            Customer.deleted_at == None
        ).count()
        growth_history.append(m_count)
        
    return calculate_trend(growth_history)
