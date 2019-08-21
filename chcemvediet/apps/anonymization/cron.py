from poleno.cron import cron_job

from .normalization import normalize_attachment
from .recognition import recognize_attachment
from .anonymization import anonymize_attachment
from .finalization import finalize_attachment


@cron_job(run_every_mins=1)
def anonymization():
    normalize_attachment()
    recognize_attachment()
    anonymize_attachment()
    finalize_attachment()
