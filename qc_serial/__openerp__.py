# -*- coding: utf-8 -*-


{
    "name" : "Bista QC Serial",
    "version" : "1.0",
    "sequence" : 1,
    "author" : "Bista Solutions",
    "category" : "Localization/Mexico",
    "description" : """This module add a QC serial
    """,
    "website" : "http://www.bistasolutions.com/",
    "license" : "AGPL-3",
    "depends" : [
        "stock"
    ],
    "demo" : [],
    "data" : [
        "views/qc_serial_view.xml",
        "views/serial_sequence.xml",
        "wizard/transfer_details.xml",
        "security/qc_serial_security.xml",
        "report/print_barcode.xml",
    ],
    "installable" : True,
}
