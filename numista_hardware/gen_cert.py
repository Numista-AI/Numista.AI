"""
Generates a self-signed SSL cert for localhost so the Flask hardware server
can run on https://localhost:5000, which Chrome allows from HTTPS pages.

Run once:  python gen_cert.py
Then restart auto_capture.py — it will auto-detect localhost.crt / localhost.key.
"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import datetime, ipaddress, pathlib

key = rsa.generate_private_key(
    public_exponent=65537, key_size=2048, backend=default_backend()
)

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.datetime.utcnow())
    .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    )
    .sign(key, hashes.SHA256(), default_backend())
)

here = pathlib.Path(__file__).parent
cert_path = here / "localhost.crt"
key_path  = here / "localhost.key"

cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
key_path.write_bytes(
    key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption(),
    )
)
print(f"✅ Certificate: {cert_path}")
print(f"✅ Key:         {key_path}")
print()
print("Next steps:")
print("  1. Trust the cert in Chrome: navigate to localhost.crt and follow prompts,")
print("     OR use chrome://flags/#allow-insecure-localhost (easier for testing)")
print("  2. Restart auto_capture.py — it will auto-load the cert.")
