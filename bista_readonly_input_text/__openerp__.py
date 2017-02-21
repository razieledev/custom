{
    'name': 'Readonly input text field',
    'version': '1.0',
    'category': 'General',
    "sequence": 16,
    'description': """
		Readonly input text field for Form View.
		
		This plugin genrate input value non editable and after auto change value insert on database.
		
		Add this name "readonly_text" on text field at widget.		
		
		<field name="anyfield" widget="readonly_text"/>
	""",
    'author': 'Bista Solutions Pvt. Ltd.',
    'depends': ['base', 'web'],
    'init_xml': [],
    'data': [
        'views/readonly_text.xml',
    ],
    'qweb': [
        'static/src/xml/readonly_text.xml',
    ],
    'demo_xml': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
