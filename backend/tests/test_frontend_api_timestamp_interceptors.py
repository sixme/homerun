"""Secondary axios clients must share UTC timestamp normalization.

Long-timeout clients used to create bare axios instances without the
normalizeUtcTimestampsInPlace interceptor, so naive ISO timestamps from
those routes would parse as local time in the browser.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES = REPO_ROOT / "frontend" / "src" / "services"

SECONDARY_CLIENTS = (
    "apiBacktest.ts",
    "apiFillModel.ts",
    "apiDataset.ts",
    "apiTopicCatalog.ts",
    "apiProviders.ts",
    "apiReverseEngineer.ts",
    "discoveryApi.ts",
    "eventsApi.ts",
)


def test_api_client_exports_attach_helper():
    text = (SERVICES / "apiClient.ts").read_text(encoding="utf-8")
    assert "export function attachApiInterceptors" in text
    assert "normalizeUtcTimestampsInPlace" in text


def test_secondary_api_clients_attach_shared_interceptors():
    for name in SECONDARY_CLIENTS:
        text = (SERVICES / name).read_text(encoding="utf-8")
        assert "attachApiInterceptors" in text, f"{name} missing attachApiInterceptors"
        assert "axios.create" in text, f"{name} should still own its timeout client"
