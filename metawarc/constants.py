

MIME_MAP = {'application/msword' : 'doc',
            'application/vnd.ms-excel' : 'xls',
            'application/vnd.ms-powerpoint' : 'ppt',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document' : 'docx',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' : 'xlsx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation' : 'pptx',
            'application/pdf' : 'pdf',
            'application/x-pdf' : 'pdf',
            'image/png' : 'png',
            'image/jpeg' : 'jpg'
            }

MIME_PATTERNS = list(MIME_MAP.keys())

XFIELDMAP = {'author' : 'creator', 'comment.Company' : 'Company', 'producer' : 'Application', 'creation_date' : 'created'}


# File types supported
MS_OLE_FILES = ['xls', 'doc', 'ppt']
MS_XML_FILES  = ['xlsx', 'docx', 'pptx']
IMAGE_FILES  = ['jpg', 'jpeg', 'png', 'jp2', 'tiff']
ADOBE_FILES = ['pdf',]

SUPPORTED_FILE_TYPES = MS_OLE_FILES + MS_XML_FILES + IMAGE_FILES + ADOBE_FILES

DEFAULT_OPTIONS = {'encoding' : 'utf8',
                   'delimiter' : ',',
                   'limit' : 1000
                   }
