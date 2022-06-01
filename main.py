import datetime
import json
import eml_parser


def json_serial(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial


with open('test/0_HJqO8GiDxgfkCfd2EWk-PV5RauFjgRHWKp5S6Qo6AjscIKsEzQXjaxdlq07v4KqC-Jij0jAWXTnivO6SiRcwDw==.eml', 'rb') as fhdl:
    raw_email = fhdl.read()


ep = eml_parser.EmlParser()
parsed_eml = ep.decode_email_bytes(raw_email)


print(parsed_eml['header']['subject'])
print(parsed_eml['header']['date'])



