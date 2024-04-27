from odoo import api, fields, models, _, tools
import xmlrpc.client
from odoo.exceptions import UserError, ValidationError

class Odoo8Connection(models.Model):
    _name = "odoo8.connection"

    url = fields.Char(string='URL')
    username = fields.Char(string='User name')
    password = fields.Char(string='Password')
    dbname = fields.Char(string='Database')

    def test_connection(self):

        for data in self:
            url = data.url
            db = data.dbname
            username = data.username
            password = data.password
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            sd_uid = common.authenticate(db, username, password, {})
            if sd_uid:
                raise ValidationError(
                _("Connection Success."))
            else:
                raise ValidationError(
                    _('Connection Fail.'))

    def get_connection_data(self):

        sd_uid = url = db = password = False
        for data in self:

            url = data.url
            db = data.dbname
            username = data.username
            password = data.password
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            sd_uid = common.authenticate(db, username, password, {})
            if sd_uid:
                return sd_uid, url, db, password
            else:
                return sd_uid, url, db, password
        else:
            return sd_uid, url, db, password