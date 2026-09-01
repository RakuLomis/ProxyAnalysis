"""Deterministic privacy-preserving URL identities and endpoint roles."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import ipaddress
from urllib.parse import urlsplit, urlunsplit


URL_ALIGNMENT_SCHEMA_VERSION = 1
FAKE_IP_NETWORK = ipaddress.ip_network("198.18.0.0/15")


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class UrlIdentity:
    resource_url_hash: str
    normalized_url_hash: str | None
    scheme: str | None
    host: str | None
    path_depth: int | None
    has_query: bool | None
    url_parse_status: str
    url_parse_reason: str | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def url_identity(url: str) -> UrlIdentity:
    exact_hash = stable_hash(url)
    try:
        parsed = urlsplit(url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError("missing_scheme_or_host")
        scheme = parsed.scheme.lower()
        host = parsed.hostname.encode("idna").decode("ascii").lower()
        port = parsed.port
        default_port = (scheme == "http" and port == 80) or (
            scheme == "https" and port == 443
        )
        rendered_host = f"[{host}]" if ":" in host else host
        netloc = rendered_host if port is None or default_port else f"{rendered_host}:{port}"
        path = parsed.path or "/"
        canonical = urlunsplit((scheme, netloc, path, "", ""))
        return UrlIdentity(
            resource_url_hash=exact_hash,
            normalized_url_hash=stable_hash(canonical),
            scheme=scheme,
            host=host,
            path_depth=len([part for part in path.split("/") if part]),
            has_query=bool(parsed.query),
            url_parse_status="parsed",
            url_parse_reason=None,
        )
    except (TypeError, ValueError, UnicodeError) as exc:
        return UrlIdentity(
            resource_url_hash=exact_hash,
            normalized_url_hash=None,
            scheme=None,
            host=None,
            path_depth=None,
            has_query=None,
            url_parse_status="failed",
            url_parse_reason=str(exc),
        )


def host_matches_domain(host: str | None, domain: str) -> bool | None:
    if host is None:
        return None
    normalized = domain.strip(".").lower()
    return host == normalized or host.endswith("." + normalized)


def is_fake_ip(value: str | None) -> bool:
    if not value:
        return False
    try:
        return ipaddress.ip_address(value) in FAKE_IP_NETWORK
    except ValueError:
        return False


def endpoint_role(value: str | None, *, side: str, outcome: str | None) -> str:
    if not value:
        return "unknown"
    if is_fake_ip(value):
        return "fake_ip"
    if side == "post" and outcome == "proxy":
        return "proxy_endpoint"
    if outcome == "direct":
        return "direct_origin_candidate"
    return "unknown"

