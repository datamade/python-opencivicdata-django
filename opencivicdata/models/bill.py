from django.db import models
from django.contrib.postgres.fields import ArrayField

from .base import (OCDBase, LinkBase, OCDIDField, RelatedBase, RelatedEntityBase, MimetypeLinkBase,
                   IdentifierBase)
from .people_orgs import Organization
from .jurisdiction import LegislativeSession
from .. import common


class Bill(OCDBase):
    id = OCDIDField(ocd_type='bill')
    legislative_session = models.ForeignKey(LegislativeSession, related_name='bills')
    identifier = models.CharField(max_length=100)

    title = models.TextField()

    from_organization = models.ForeignKey(Organization, related_name='bills', null=True)
    classification = ArrayField(base_field=models.TextField(), blank=True, default=list)      # check that array values are in enum?
    subject = ArrayField(base_field=models.TextField(), blank=True, default=list)

    def __str__(self):
        return '{} in {}'.format(self.identifier, self.legislative_session)

    class Meta:
        index_together = [
            ['from_organization', 'legislative_session', 'identifier'],
        ]


class BillAbstract(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='abstracts')
    abstract = models.TextField()
    note = models.TextField(blank=True)
    date = models.TextField(max_length=10, blank=True)  # YYYY[-MM[-DD]]


class BillTitle(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='other_titles')
    title = models.TextField()
    note = models.TextField(blank=True)


class BillIdentifier(IdentifierBase):
    bill = models.ForeignKey(Bill, related_name='other_identifiers')
    note = models.TextField(blank=True)


class BillAction(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='actions')
    organization = models.ForeignKey(Organization, related_name='actions')
    description = models.TextField()
    date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    classification = ArrayField(base_field=models.TextField(), blank=True, default=list)     # enum
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']


class BillActionRelatedEntity(RelatedEntityBase):
    action = models.ForeignKey(BillAction, related_name='related_entities')


class RelatedBill(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='related_bills')
    related_bill = models.ForeignKey(Bill, related_name='related_bills_reverse', null=True)
    identifier = models.CharField(max_length=100)
    # not a FK in case we don't know the session yet
    legislative_session = models.CharField(max_length=100)
    relation_type = models.CharField(max_length=100, choices=common.BILL_RELATION_TYPE_CHOICES)

    def __str__(self):
        return 'relationship of {} to {} ({})'.format(self.bill, self.related_bill,
                                                      self.relation_type)


class BillSponsorship(RelatedEntityBase):
    bill = models.ForeignKey(Bill, related_name='sponsorships')
    primary = models.BooleanField(default=False)
    classification = models.CharField(max_length=100)   # enum?

    def __str__(self):
        return '{} ({}) sponsorship of {}'.format(self.name, self.entity_type, self.bill)


class BillDocument(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='documents')
    note = models.CharField(max_length=300)
    date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]


class BillVersion(RelatedBase):
    bill = models.ForeignKey(Bill, related_name='versions')
    note = models.CharField(max_length=300)
    date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]


class BillDocumentLink(MimetypeLinkBase):
    document = models.ForeignKey(BillDocument, related_name='links')


class BillVersionLink(MimetypeLinkBase):
    version = models.ForeignKey(BillVersion, related_name='links')


class BillSource(LinkBase):
    bill = models.ForeignKey(Bill, related_name='sources')
