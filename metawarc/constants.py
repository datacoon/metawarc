# Common mime types to extension mappings
# Used to dump files
# Sources: 
# - documentation at https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
# - data from API https://ckan.govdata.de 
MIME_EXT_MAP = {
'application/atom+xml' : 'xml',
'application/epub+zip' : 'epub',
'application/gml+xml' : 'gml',
'application/gzip' : 'gz',
'application/java-archive' : 'jar',
'application/javascript' : 'js',
'application/json' : 'json',
'application/ld+json' : 'jsonld',
'application/msword' : 'doc',
'application/octet-stream' : 'bin',
'application/pdf' : 'pdf',
'application/rar' : 'rar',
'application/rdf+xml' : 'rdf',
'application/rss+xml' : 'xml',
'application/rtf' : 'rtf',
'application/vnd.android.package-archive' : 'apk',
'application/vnd.geo+json' : 'geojson',
'application/vnd.google-earth.kml+xml' : 'kml',
'application/vnd.google-earth.kmz' : 'kmz',
'application/vnd.ms-excel' : 'xls',
'application/vnd.ms-fontobject' : 'eot',
'application/vnd.oasis.opendocument.presentation' : 'ogp',
'application/vnd.oasis.opendocument.spreadsheet' : 'ods',
'application/vnd.oasis.opendocument.text' : 'odt',
'application/vnd.ogc.wfs_xml' : 'wfs',
'application/vnd.ogc.wms_xml' : 'wms',
'application/vnd.rar' : 'rar',
'application/vnd.visio' : 'vsd',
'application/x-font-woff' : 'woff',
'application/x-7z-compressed' : '7z',
'application/x-bzip' : 'bz',
'application/x-bzip2' : 'bz2',
'application/x-font-ttf' : 'ttf',
'application/x-javascript' : 'js',
'application/x-pdf' : 'pdf',
'application/x-shapefile' : 'shp',
'application/x-tar' : 'tar',
'application/x-turtle' : 'ttl',
'application/x-x509-ca-cert' : 'crt',
'application/x-zip-compressed' : 'zip',
'application/xml' : 'xml',
'application/zip' : 'zip',

'audio/mp3' : 'mp3',
'audio/mpeg' : 'mp3',
'audio/ogg' : 'ogg',
'audio/x-wav' : 'wav',
'audio/wav' : 'wav',
'audio/webm' : 'weba',

'dwg/dxf' : 'dxf',

'font/otf' : 'otf',
'font/ttf' : 'ttf',
'font/woff' : 'woff',
'font/woff2' : 'woff2',

'image/bmp' : 'bmp',
'image/gif' : 'gif',
'image/jpeg' : 'jpg',
'image/png' : 'png',
'image/svg+xml' : 'svg',
'image/tiff' : 'tif',
'image/vnd.dxf' : 'dxf',
'image/webp' : 'webp',
'image/x-icon' : 'ico',

'text/calendar' : 'ics',
'text/css' : 'css',
'text/csv' : 'csv',
'text/html' : 'html',
'text/plain' : 'txt',
'text/xml' : 'xml',

'video/mp2t' : 'ts',
'video/mp4' : 'mp4',
'video/ogg' : 'ogv',
'video/quicktime' : 'mov',
'video/webm' : 'webm',
'video/x-ms-wmv' : 'wmv',
'video/x-msvideo' : 'avi'
}


# Short list of mime types to extenisions map 
# Used to extract metadata from office files, pdf and images
MIME_SHORT_MAP = {
    "application/msword": "doc",
    "application/vnd.ms-excel": "xls",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    "docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
    "xlsx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation":
    "pptx",
    "application/pdf": "pdf",
    "application/x-pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
}

MIME_PATTERNS = list(MIME_MAP.keys())

XFIELDMAP = {
    "author": "creator",
    "comment.Company": "Company",
    "producer": "Application",
    "creation_date": "created",
}

# File types supported
MS_OLE_FILES = ["xls", "doc", "ppt"]
MS_XML_FILES = ["xlsx", "docx", "pptx"]
IMAGE_FILES = ["jpg", "jpeg", "png", "jp2", "tiff"]
ADOBE_FILES = [
    "pdf",
]

SUPPORTED_FILE_TYPES = MS_OLE_FILES + MS_XML_FILES + IMAGE_FILES + ADOBE_FILES

DEFAULT_OPTIONS = {"encoding": "utf8", "delimiter": ",", "limit": 1000}
