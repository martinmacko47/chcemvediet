import sys
from optparse import make_option

import magic
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from poleno.attachments.models import Attachment
from poleno.utils.misc import squeeze
from chcemvediet.apps.anonymization.models import AttachmentFinalization
from chcemvediet.apps.inforequests.models import Action


class Command(BaseCommand):
    args = u'attachment_id [file]'
    help = squeeze(u"""
            Creates anonymization for the specified Attachment. The content source is file, that can
            be passed as an argument, or stdin. Preferred source is file. If file is not specified
            and stdin is empty, the command will fail. Anonymization created this way will be marked
            as successful. Only one successful anonymization can be assigned to the Attachment.
            """)

    option_list = BaseCommand.option_list + (
        make_option(u'--content_type',
                    help=squeeze(u"""
                            Content type of file, e.g. "application/pdf". Automatically guessed from
                            the file content if not specified.
                            """)
                    ),
        make_option(u'--debug',
                    default=u'',
                    help=u'Debug message to the newly created anonymization. Empty by default.'
                    ),
        make_option(u'--force',
                    action=u'store_true',
                    help=squeeze(u"""
                            The command refuses to anonymize attachment if a successful
                            anonymization already exists. This flag disables this check. Deletes all
                            existing successful anonymizations and creates new one. Unsuccessful
                            anonymizations will stay unaffected.
                            """)
                    ),
    )

    def handle(self, *args, **options):
        if not args:
            raise CommandError(u'attachment_anonymization takes at least 1 argument (0 given).')
        elif len(args) > 2:
            raise CommandError(
                u'attachment_anonymization takes at most 2 arguments ({} given).'.format(len(args))
            )

        attachment_pk = args[0]
        try:
            attachment = Attachment.objects.attached_to(Action).get(pk=attachment_pk)
        except (Attachment.DoesNotExist, ValueError):
            raise CommandError(
                u'Attachment instance with pk "{}" does not exist.'.format(attachment_pk)
            )
        attachments_finalization = (AttachmentFinalization.objects
                                    .filter(attachment=attachment)
                                    .successful())
        if not options[u'force'] and attachments_finalization:
            raise CommandError(squeeze(u"""
                    Anonymization files already exist. Use the --force option to overwrite
                    them.
                    """))

        if len(args) == 2:
            filename = args[1]
            try:
                with open(filename, u'rb') as file:
                    content = file.read()
            except IOError as e:
                raise CommandError(u'Could not open file: {}.'.format(e))
        else:
            content = sys.stdin.read()
            if not content:
                raise CommandError(u'No content given.')

        attachments_finalization.delete()
        AttachmentFinalization.objects.create(
            attachment=attachment,
            successful=True,
            file=ContentFile(content),
            content_type=options[u'content_type'] or magic.from_buffer(content, mime=True),
            debug=options[u'debug'],
        )
