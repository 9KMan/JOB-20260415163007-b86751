"""Routes package initialization."""
from app.routes.procurement import procurement_bp
from app.routes.goods_receiving import goods_receiving_bp
from app.routes.production import production_bp
from app.routes.packaging import packaging_bp
from app.routes.sales import sales_bp
from app.routes.financial import financial_bp
from app.routes.reporting import reporting_bp

__all__ = [
    'procurement_bp',
    'goods_receiving_bp',
    'production_bp',
    'packaging_bp',
    'sales_bp',
    'financial_bp',
    'reporting_bp'
]