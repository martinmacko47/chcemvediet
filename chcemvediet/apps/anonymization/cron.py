from poleno.cron import cron_job

from .normalization import normalize_attachment
from .recognition import recognize_attachment
from .anonymization_odt import anonymize_attachment_odt
from .anonymization_pdf import anonymize_attachment_pdf


@cron_job(run_every_mins=1)
def anonymization():
    normalize_attachment()
    recognize_attachment()
    anonymize_attachment_odt()
    anonymize_attachment_pdf()
