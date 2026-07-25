"""
Numista.AI OS SSL Certificate Installer & Dynamic Generator
============================================================
Generates a dynamic 2048-bit RSA self-signed SSL certificate for localhost
with SAN extension (DNS:localhost, IP:127.0.0.1) and registers it into the
Windows Current User Trusted Root Certification Authorities store via certutil.
"""

import os
import sys
import subprocess
import datetime
import ipaddress
from pathlib import Path

# Force stdout/stderr to UTF-8 on Windows
for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass

def get_cert_dir() -> Path:
    """Returns the persistent directory for local SSL certificates."""
    appdata = os.environ.get("LOCALAPPDATA")
    if appdata:
        cert_dir = Path(appdata) / "NumistaAI" / "certs"
    else:
        cert_dir = Path.home() / "NumistaAI" / "certs"
    cert_dir.mkdir(parents=True, exist_ok=True)
    return cert_dir

def generate_ssl_cert(cert_path: Path, key_path: Path) -> bool:
    """Generates a dynamic RSA key and self-signed cert with SubjectAlternativeName."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        print(f"[CERT] Generating new SSL certificate for localhost...")
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Numista.AI Hardware Agent"),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
            .add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            )
            .add_extension(
                x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),
                critical=False,
            )
            .sign(key, hashes.SHA256(), default_backend())
        )

        cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )
        print(f"[CERT] ✅ Generated certificate: {cert_path}")
        print(f"[CERT] ✅ Generated key:         {key_path}")
        return True
    except Exception as e:
        print(f"[CERT] ❌ Error generating SSL certificate: {e}", file=sys.stderr)
        return False

def register_cert_in_windows_store(cert_path: Path) -> bool:
    """Registers localhost.crt in Windows Trusted Root Certification Authorities store."""
    if sys.platform != "win32":
        print("[CERT] Skipping certutil — platform is not Windows.")
        return True

    print(f"[CERT] Trusting {cert_path.name} in Windows Root CA store (certutil -user -addstore Root)...")
    try:
        cmd = ["certutil", "-user", "-addstore", "Root", str(cert_path)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode == 0:
            print("[CERT] ✅ Certificate successfully added to Windows Root CA store.")
            return True
        else:
            print(f"[CERT] ⚠️ certutil returned non-zero code ({res.returncode}): {res.stderr or res.stdout}")
            # Try system-wide fallback
            cmd_sys = ["certutil", "-addstore", "Root", str(cert_path)]
            res_sys = subprocess.run(cmd_sys, capture_output=True, text=True, check=False)
            if res_sys.returncode == 0:
                print("[CERT] ✅ Certificate added to system Root CA store.")
                return True
            return False
    except Exception as e:
        print(f"[CERT] ❌ certutil execution failed: {e}", file=sys.stderr)
        return False

def ensure_ssl_cert() -> tuple[Path, Path]:
    """Ensures a valid SSL cert exists and is registered. Returns (cert_path, key_path)."""
    cert_dir = get_cert_dir()
    cert_path = cert_dir / "localhost.crt"
    key_path = cert_dir / "localhost.key"

    # Also check local numista_hardware fallback directory
    here = Path(__file__).parent
    local_cert = here / "localhost.crt"
    local_key = here / "localhost.key"

    if not cert_path.exists() or not key_path.exists():
        if local_cert.exists() and local_key.exists():
            cert_path = local_cert
            key_path = local_key
        else:
            generate_ssl_cert(cert_path, key_path)

    register_cert_in_windows_store(cert_path)
    return cert_path, key_path

if __name__ == "__main__":
    c_path, k_path = ensure_ssl_cert()
    print(f"[CERT] Ready: {c_path}")
