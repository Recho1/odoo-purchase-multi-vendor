{
    'name': 'Purchase Multi Vendor',
    'version': '19.0.1.0.0',
    'summary': 'Assign RFQs to multiple vendors',
    'description': """
        Adds the ability to assign a single RFQ to multiple vendors,
        collect bids from each vendor, select a winning bid to generate
        a Purchase Order, and manage employee purchase requests that
        feed into the RFQ process.
    """,
    'author': 'Racheal Acio',
    'category': 'Purchases',
    'depends': ['purchase'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/purchase_order_views.xml',
        'views/purchase_request_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
