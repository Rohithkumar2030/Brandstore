"""
Custom SMTP email backend that uses certifi's CA bundle.

Fixes 'SSL: CERTIFICATE_VERIFY_FAILED' on macOS with Python 3.13+
where the system CA certificates are not found by default.
"""
import ssl

import certifi
from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property


class CertifiEmailBackend(SMTPBackend):
    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            ctx = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            ctx.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
            return ctx
        return ssl.create_default_context(cafile=certifi.where())
