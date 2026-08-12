{
    'name': 'Purchase Multi Vendor',
    'version': '19.0.1.0.0',
    'summary': 'Assign RFQs to multiple vendors',
    'description': """
        Adds the ability to assign a single RFQ to multiple vendors,
        collect bids from each vendor, and select a winning bid to
        generate a Purchase Order.
    """,
    'author': 'Racheal Acio',
    'category': 'Purchases',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
