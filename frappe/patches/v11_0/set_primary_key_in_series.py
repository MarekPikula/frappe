import frappe

def execute():
    keys_encountered = set()
    #if current = 0, simply delete the key as it'll be recreated on first entry
    frappe.db.sql('delete from `tabSeries` where current = 0')
    duplicate_keys = frappe.db.sql('''
        SELECT distinct name, current
        from
            `tabSeries`
        where
            name in (Select name from `tabSeries` group by name having count(name) > 1)
    ''', as_dict=True)
    for row in duplicate_keys:
        if row.name in keys_encountered:
            frappe.throw('''
Key {row.name} appears twice in `tabSeries` with different values.
Kindly remove the faulty one manually before continuing
            '''.format(row=row))
        frappe.db.sql('delete from `tabSeries` where name = %(key)s', {
            'key': row.name
        })
        if row.current:
            frappe.db.sql('insert into `tabSeries`(`name`, `current`) values (%(name)s, %(current)s)', row)
        keys_encountered.add(row.name)
    frappe.db.commit()
    frappe.db.sql('ALTER table `tabSeries` ADD PRIMARY KEY IF NOT EXISTS (name)')
