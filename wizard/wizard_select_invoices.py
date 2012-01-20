# coding=utf-8

#    Copyright (C) 2008-2011  Luis Falcon

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard


class InvoiceToPay(ModelView):

    _name = 'account.voucher.invoice_to_pay'

    name = fields.Char('Name')
    party = fields.Many2One('party.party', 'Party')
    line_ids = fields.Many2Many('account.move.line', None, None, 'Account Moves')

InvoiceToPay()


class SelectInvoices(Wizard):
    'Open Chart Of Account'
    _name = 'account.voucher.select_invoices'

    def search_lines(self,data):
        res = {}
        voucher_obj = self.pool.get('account.voucher')
        voucher = voucher_obj.browse(data['id'])
        move_line = self.pool.get('account.move.line')

        if voucher.voucher_type == 'receipt':
            account_types = ['receivable']
        else:
            account_types = ['payable']

        line_domain = [
                    ('party','=',voucher.party.id),
                    ('account.kind','in',account_types),
                    ('state','=','valid'),
                    ('reconciliation','=',False)]

        move_ids = move_line.search(line_domain)
        res['line_ids'] = move_ids
        return res

    states = {
        'init': {
            'actions': ['search_lines'],
            'result': {
                'type': 'form',
                'object': 'account.voucher.invoice_to_pay',
                'state': [
                    ('end', 'Cancel', 'tryton-cancel'),
                    ('open', 'Open', 'tryton-ok', True),
                ],
            },
        },
        'open': {
            'result': {
                'type': 'action',
                'action': '_action_add_lines',
                'state': 'end',
            },
        },
    }



    def _action_add_lines(self, data):
        res = {}
        total_credit = 0
        total_debit = 0
        voucher_line_obj = self.pool.get('account.voucher.line')
        voucher = self.pool.get('account.voucher').browse(data['id'])
        move_line_obj = self.pool.get('account.move.line')
        move_ids = data['form']['line_ids'][0][1]

        for line in move_line_obj.browse(move_ids):
            total_credit += line.credit
            total_debit += line.debit
            if line.credit:
                line_type = 'cr'
                amount = line.credit
            else:
                amount = line.debit
                line_type = 'dr'

            new_line_ids = voucher_line_obj.create({
                'voucher_id':data['id'],
                'name': line.name,
                'account_id':line.account.id,
                'amount_original': amount,
                'amount_unreconciled':amount,
                'line_type': line_type,
                'move_line_id': line.id,
            })
        voucher.write(data['id'],{
        })

        return res

#    voucher_id = fields.Many2One('account.voucher', 'Voucher')
#    name = fields.Char('Name')
#    account_id = fields.Many2One('account.account', 'Account')
#    amount = fields.Float('Amount')
#    line_type = fields.Selection([
#        ('cr', 'Credit'),
#        ('dr', 'Debit'),
#        ], 'Type', select='1')
#    move_line_id = fields.Many2One('account.move.line', 'Move Line')
#    amount_original = fields.Float('Original Amount')
#    amount_unreconciled = fields.Float('Unreconciled amount')




SelectInvoices()

