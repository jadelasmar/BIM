from django.db import migrations


def backfill_party_fields(apps, schema_editor):
    Client = apps.get_model("bim_stock", "Client")
    Supplier = apps.get_model("bim_stock", "Supplier")
    InternalParty = apps.get_model("bim_stock", "InternalParty")
    ReservationRecord = apps.get_model("bim_stock", "ReservationRecord")
    IssueRecord = apps.get_model("bim_stock", "IssueRecord")
    RepairRecord = apps.get_model("bim_stock", "RepairRecord")

    created_clients = []
    created_parties = []
    matched = {"client": 0, "supplier": 0}

    # Reservations: reserved_for text -> existing Client, else existing
    # Supplier, else a new Client with that name (a name like a business is not
    # a department).
    for reservation in ReservationRecord.objects.all():
        name = (reservation.reserved_for or "").strip()
        if not name:
            continue
        client = Client.objects.filter(name__iexact=name).first()
        supplier = None
        if client is None:
            supplier = Supplier.objects.filter(name__iexact=name).first()
        if client is None and supplier is None:
            client = Client.objects.create(name=name)
            created_clients.append(name)
        elif client is not None:
            matched["client"] += 1
        else:
            matched["supplier"] += 1

        if client is not None:
            reservation.reserved_for_type = "client"
            reservation.reserved_for_client = client
        else:
            reservation.reserved_for_type = "supplier"
            reservation.reserved_for_supplier = supplier
        reservation.save(
            update_fields=(
                "reserved_for_type",
                "reserved_for_client",
                "reserved_for_supplier",
            )
        )

    # Temporary assignments: issued_to text -> Internal party (department,
    # since free text cannot tell a person from a team).
    for issue in IssueRecord.objects.all():
        name = (issue.issued_to or "").strip()
        if not name:
            continue
        party, created = InternalParty.objects.get_or_create(
            kind="department",
            name=name,
        )
        if created:
            created_parties.append(name)
        issue.assigned_to = party
        issue.save(update_fields=("assigned_to",))

    # Repairs: technician text -> matching Supplier as vendor, otherwise kept
    # in notes. Repairs that came from a client return get that as their source.
    moved_to_notes = 0
    vendors_matched = 0
    for repair in RepairRecord.objects.all():
        technician = (repair.technician or "").strip()
        if technician:
            supplier = Supplier.objects.filter(name__iexact=technician).first()
            if supplier is not None:
                repair.vendor = supplier
                vendors_matched += 1
            else:
                line = f"Technician: {technician}"
                repair.notes = f"{repair.notes}\n{line}" if repair.notes else line
                moved_to_notes += 1
        if repair.client_return_id:
            repair.source = "client_return"
            repair.source_client_id = repair.client_return.client_id
        repair.save(update_fields=("vendor", "notes", "source", "source_client"))

    print(
        "\n  Party backfill: "
        f"{len(created_clients)} client(s) created from reservation names "
        f"{created_clients}, "
        f"{matched['client']} reservation(s) matched an existing client, "
        f"{matched['supplier']} matched a supplier, "
        f"{len(created_parties)} internal part(y/ies) created {created_parties}, "
        f"{vendors_matched} repair vendor(s) matched, "
        f"{moved_to_notes} technician name(s) moved to notes.",
        end="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("bim_stock", "0034_internal_parties_and_party_fields"),
    ]

    operations = [
        migrations.RunPython(backfill_party_fields, migrations.RunPython.noop),
    ]
