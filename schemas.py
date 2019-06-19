from __future__ import unicode_literals

import itertools
from marshmallow_enum import EnumField

from indico.core.db.sqlalchemy.principals import PrincipalType
from indico.core.db.sqlalchemy.protection import ProtectionMode
from indico.core.db.sqlalchemy.links import LinkType
from indico.core.marshmallow import mm
from indico.modules.attachments.models.attachments import Attachment, AttachmentType
from indico.modules.events.contributions.models.contributions import Contribution
from indico.modules.events.contributions.models.subcontributions import SubContribution
from indico.modules.events.notes.models.notes import EventNote
from indico.modules.events import Event
from indico.modules.events.models.events import EventType
from indico.modules.events.models.persons import EventPersonLink

import tika    # for test purposes
from tika import parser


def _get_location(obj):
    if obj.venue_name and obj.room_name:
        return '{}: {}'.format(obj.venue_name, obj.room_name)
    elif obj.venue_name or obj.room_name:
        return obj.venue_name or obj.room_name
    else:
        return None


def _get_location_subcontribution(subcontribution):
    contribution_id = subcontribution.contribution_id
    obj = Contribution.get_one(contribution_id)
    if obj.venue_name and obj.room_name:
        return '{}: {}'.format(obj.venue_name, obj.room_name)
    elif obj.venue_name or obj.room_name:
        return obj.venue_name or obj.room_name
    else:
        return None


def _get_identifiers(principal):
    if principal.principal_type == PrincipalType.user:
        # Instead of using the email this uses `User:ID`.
        # Since the user can change the email this is better as
        # it will ensure that only this given Indico user has access.
        # If you want to stick with email, simply replace it with
        # 'User:{}'.format(principal.email)
        yield principal.identifier
        yield '{}'.format(principal.email)
    elif principal.principal_type == PrincipalType.event_role:
        for user in principal.members:
            # same thing here
            yield user.identifier
            yield '{}'.format(principal.email)
    elif principal.is_group:
        yield principal.identifier


def _get_category_path(obj):
    if isinstance(obj, Event):
        event_id = obj.id
    elif isinstance(obj, Attachment):
        event_id = obj.folder.event.id
    else: 
        event_id = obj.event.id
    event = Event.get_one(event_id)
    return event.category.chain_titles[1:]


def _get_event_acl(event):
    if event.effective_protection_mode == ProtectionMode.public:
        acl = []
    else:
        acl = set(itertools.chain.from_iterable(_get_identifiers(x.principal) for x in event.acl_entries))
    return {'read': sorted(acl), 'owner': [], 'update': [], 'delete': []}


def _get_attachment_acl(attachment):
    linked_object = attachment.folder.object

    if attachment.is_self_protected:
        principals = {p for p in attachment.acl} | set(linked_object.get_manager_list(recursive=True))
    elif attachment.is_inheriting and attachment.folder.is_self_protected:
        principals = {p for p in attachment.folder.acl} | set(linked_object.get_manager_list(recursive=True))
    else:
        principals = linked_object.get_access_list()

    acl = set(itertools.chain.from_iterable(_get_identifiers(x) for x in principals))
    return {'read': sorted(acl), 'owner': [], 'update': [], 'delete': []}


def _get_contribution_acl(obj):

    if obj.is_self_protected:
        principals = {p for p in obj.acl} | set(obj.get_manager_list(recursive=True))
    elif obj.is_inheriting and obj.is_self_protected:
        principals = {p for p in obj.acl} | set(obj.get_manager_list(recursive=True))
    else:
        principals = obj.get_access_list()

    acl = set(itertools.chain.from_iterable(_get_identifiers(x) for x in principals))
    return {'read': sorted(acl), 'owner': [], 'update': [], 'delete': []}


def _get_subcontribution_acl(subcontribution):
    contribution_id = subcontribution.contribution_id
    obj = Contribution.get_one(contribution_id)

    if obj.is_self_protected:
        principals = {p for p in obj.acl} | set(obj.get_manager_list(recursive=True))
    elif obj.is_inheriting and obj.is_self_protected:
        principals = {p for p in obj.acl} | set(obj.get_manager_list(recursive=True))
    else:
        principals = obj.get_access_list()

    acl = set(itertools.chain.from_iterable(_get_identifiers(x) for x in principals))
    return {'read': sorted(acl), 'owner': [], 'update': [], 'delete': []}


def _get_eventnote_acl(eventnote):
    event_id = eventnote.event_id
    contribution_id = eventnote.subcontribution.contribution_id if eventnote.subcontribution.id else eventnote.contribution.id
    if contribution_id:
        obj = Contribution.get_one(contribution_id)
        return _get_contribution_acl(obj)
    else:
        obj = Event.get_one(event_id)
        return  _get_event_acl(obj)


def _get_attachment_content(attachment):
    if attachment.type == AttachmentType.file:
        tika.initVM()   # for test purposes
        parsedfile = parser.from_file(attachment.absolute_download_url) #, serverEndpoint=self.tika_server)
        return parsedfile["content"]
    else:
        return None


def _get_attachment_contributionid(attachment):
    return attachment.folder.contribution.id if attachment.folder.link_type == LinkType.contribution else None


def _get_attachment_subcontributionid(attachment):
    return attachment.folder.subcontribution.id if attachment.folder.link_type == LinkType.subcontribution else None


def _get_eventnote_contributionid(eventnote):
    return eventnote.subcontribution.contribution.id if eventnote.subcontribution.id else eventnote.contribution.id


class PersonLinkSchema(mm.Schema):
    # Not using a ModelSchema here so this can be used for contribution person links etc. as well!
    name = mm.String(attribute='full_name')
    affiliation = mm.String()

    class Meta:
        model = EventPersonLink
        fields = ('name', 'affiliation')


class EventSchema(mm.ModelSchema):
    url = mm.String(attribute='external_url')
    category_path = mm.Function(_get_category_path)
    event_type = EnumField(EventType, attribute='type_')
    creation_date = mm.DateTime(attribute='created_dt')
    start_date = mm.DateTime(attribute='start_dt')
    end_date = mm.DateTime(attribute='end_dt')
    location = mm.Function(_get_location)
    speakers_chairs = mm.Nested(PersonLinkSchema, attribute='person_links', many=True)
    _access = mm.Function(_get_event_acl)

    class Meta:
        model = Event
        fields = ('_access', 'category_path', 'creation_date', 'description', 'end_date', 'event_type', 'id',
                  'location', 'speakers_chairs', 'start_date', 'title', 'url')


class AttachmentSchema(mm.ModelSchema):
    _access = mm.Function(_get_attachment_acl)
    category_path = mm.Function(_get_category_path)
    url = mm.String(attribute='absolute_download_url')
    name = mm.String(attribute='title')
    creation_date = mm.DateTime(attribute='modified_dt')
    filename = mm.String(attribute='file.filename')
    content = mm.String(default='Some File Content')    #Function(_get_attachment_content)
    event_id = mm.Integer(attribute='folder.event.id')
    contribution_id = mm.Function(_get_attachment_contributionid)
    subcontribution_id = mm.Function(_get_attachment_subcontributionid)


    class Meta:
        model = Event
        fields = ('_access', 'id', 'category_path', 'event_id', 'contribution_id', 'subcontribution_id', 'url',
                  'creation_date', 'filename', 'content')


class ContributionSchema(mm.ModelSchema):
    url = mm.String(attribute='event.external_url')
    category_path = mm.Function(_get_category_path)
    event_id = mm.Integer(attribute='event_id')
    creation_date = mm.DateTime(attribute='created_dt')
    start_date = mm.DateTime(attribute='start_dt')
    end_date = mm.DateTime(attribute='end_dt')
    location = mm.Function(_get_location)
    list_of_persons = mm.Nested(PersonLinkSchema, attribute='person_links', many=True)
    _access = mm.Function(_get_contribution_acl)

    class Meta:
        model = Event
        fields = ('_access', 'category_path', 'creation_date', 'description', 'end_date', 'id', 'location',
                  'event_id', 'list_of_persons', 'start_date', 'title', 'url')


class SubContributionSchema(mm.ModelSchema):
    url = mm.String(attribute='event.external_url')
    category_path = mm.Function(_get_category_path)
    event_id = mm.Integer(attribute='event.id')
    contribution_id = mm.Integer(attribute='contribution_id')
    creation_date = mm.DateTime(attribute='created_dt')
    start_date = mm.DateTime(attribute='start_dt')
    end_date = mm.DateTime(attribute='end_dt')
    location = mm.Function(_get_location_subcontribution)
    list_of_persons = mm.Nested(PersonLinkSchema, attribute='person_links', many=True)
    _access = mm.Function(_get_subcontribution_acl)

    class Meta:
        model = Event
        fields = ('_access', 'category_path', 'creation_date', 'description', 'end_date', 'id', 'location',
                  'event_id', 'contribution_id', 'list_of_persons', 'start_date', 'title', 'url')


class EventNoteSchema(mm.ModelSchema):
    url = mm.String(attribute='event.external_url')
    category_path = mm.Function(_get_category_path)
    event_id = mm.Integer(attribute='event_id')
    contribution_id = mm.Function(_get_eventnote_contributionid)
    subcontribution_id = mm.Integer(attribute='subcontribution_id')
    creation_date = mm.DateTime(attribute='current_revision.created_dt')
    content = mm.String(attribute='html')
    _access = mm.Function(_get_eventnote_acl)

    class Meta:
        model = Event
        fields = ('_access', 'category_path', 'creation_date', 'id',
                  'event_id', 'contribution_id', 'subcontribution_id', 'content', 'url')



# If you want to test this quickly, keep the code below and the file as indico/web/blueprint.py
# and go to https://yourinstance/schema-test/event/EVENTID

from indico.web.flask.wrappers import IndicoBlueprint
bp = IndicoBlueprint('test', __name__)

@bp.route('/schema-test/event/<int:event_id>/')
def event_test(event_id):
    event = Event.get_one(event_id)
    return EventSchema().jsonify(event)

@bp.route('/schema-test/attachment/<int:attachment_id>/')
def attachment_test(attachment_id):
    attachment = Attachment.get_one(attachment_id)
    return AttachmentSchema().jsonify(attachment)

@bp.route('/schema-test/contribution/<int:contribution_id>/')
def contribution_test(contribution_id):
    contribution = Contribution.get_one(contribution_id)
    return ContributionSchema().jsonify(contribution)

@bp.route('/schema-test/subcontribution/<int:subcontribution_id>/')
def subcontribution_test(subcontribution_id):
    subcontribution = SubContribution.get_one(subcontribution_id)
    return SubContributionSchema().jsonify(subcontribution)

@bp.route('/schema-test/note/<int:note_id>/')
def note_test(note_id):
    note = EventNote.get_one(note_id)
    return EventNoteSchema().jsonify(note)